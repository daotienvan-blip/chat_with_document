"""Ứng dụng FastAPI. Endpoint đồng bộ (PLAN §3)."""
from __future__ import annotations

import re
import time
import uuid
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, File, Request, Response, UploadFile
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, StreamingResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from cwd_server.api import problems
from cwd_server.api.problems import problem
from cwd_server.api.schemas import AnswerOut, ConfigOut, DocumentListOut, DocumentOut, QuestionIn
from cwd_server.container import Container
from cwd_server.core.documents.validate_upload import effective_limit_mb, validate_upload
from cwd_server.core.errors import EmptyQuestion, FileTooLarge, InvalidRequest, NotFound, QuestionTooLong
from cwd_server.platform import metrics
from cwd_server.platform.logging import request_id_var

NO_STORE = {"Cache-Control": "no-store"}
_RANGE_RE = re.compile(r"^bytes=(\d*)-(\d*)$")


def _range_error(size: int) -> JSONResponse:
    body = {"type": "urn:cwd:problem:invalid-request", "title": "Phạm vi không hợp lệ", "status": 416,
            "detail": "Phạm vi Range không hợp lệ.", "code": "INVALID_REQUEST",
            "requestId": request_id_var.get() or ""}
    return JSONResponse(body, status_code=416, media_type="application/problem+json",
                        headers={"Content-Range": f"bytes */{size}", "Cache-Control": "no-store"})


def _group(request: Request) -> str:
    p, m = request.url.path, request.method
    if p == "/api/v1/questions" and m == "POST":
        return "questions"
    if p == "/api/v1/documents" and m == "POST":
        return "uploads"
    return "other"


def create_app(c: Container) -> FastAPI:
    s = c.settings
    app = FastAPI(title="Chat với tài liệu", docs_url=None, redoc_url=None, openapi_url=None)
    problems.install(app)

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        # Proxy ghi đè X-Request-Id (S8-06); khi chạy trực tiếp (dev/demo) thì tự sinh.
        rid = request.headers.get("x-request-id") if s.trust_proxy else None
        rid = rid or uuid.uuid4().hex[:12]
        token = request_id_var.set(rid)
        t0 = time.monotonic()
        try:
            if s.rate_limit_enabled and request.url.path.startswith("/api/"):
                fwd = request.headers.get("x-forwarded-for") if s.trust_proxy else None
                client = (fwd.split(",")[0].strip() if fwd else None) or (request.client.host if request.client else "?")
                try:
                    c.rate_limiter.hit(client, _group(request))
                except Exception as e:
                    return problem(e.code, e.detail, retry_after=e.retry_after)
            try:
                resp = await call_next(request)
            except Exception as e:  # lỗi không lường trước: trả problem+json còn requestId, không lộ chi tiết
                import logging
                logging.getLogger("cwd.api").error("lỗi không lường trước", exc_info=e, extra={"event": "unhandled"})
                resp = problem("INTERNAL_ERROR")
        finally:
            request_id_var.reset(token)
        resp.headers["X-Request-Id"] = rid
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        route = request.scope.get("route")
        rname = getattr(route, "path", "other")
        metrics.HTTP_REQUESTS.labels(rname, request.method, str(resp.status_code)).inc()
        metrics.HTTP_LATENCY.labels(rname).observe(time.monotonic() - t0)
        return resp

    # ---------------- hạ tầng
    @app.get("/healthz", response_class=PlainTextResponse)
    def healthz():
        return "ok"

    @app.get("/readyz", response_class=PlainTextResponse)
    def readyz():
        try:
            c.db.ping()
            with c.db.read() as conn:
                if not c.jobs.can_enqueue(conn):
                    raise RuntimeError("không xếp được việc vào hàng đợi")
            c.store.check()
        except Exception:
            return PlainTextResponse("not ready", status_code=503)
        return "ok"

    @app.get("/metrics")
    def metrics_endpoint():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    # ---------------- nghiệp vụ
    @app.get("/api/v1/config")
    def get_config():
        return JSONResponse(ConfigOut(maxFileSizeMb=s.max_file_size_mb, maxQuestionLength=s.max_question_length,
                                      language=s.language, pollIntervalMs=s.poll_interval_ms).model_dump(),
                            headers=NO_STORE)

    @app.get("/api/v1/documents")
    def list_documents():
        items = [DocumentOut.of(d) for d in c.documents.list()]
        return JSONResponse(DocumentListOut(items=items, total=len(items)).model_dump(mode="json"), headers=NO_STORE)

    @app.post("/api/v1/documents", status_code=202)
    def upload_document(request: Request, file: UploadFile | None = File(None)):
        limit = effective_limit_mb(s.max_file_size_mb, s.hard_max_upload_mb)
        cl = request.headers.get("content-length")
        if cl and cl.isdigit() and int(cl) > limit * 1024 * 1024 + 64 * 1024:
            raise FileTooLarge(f"Tệp lớn hơn giới hạn {limit} MB.", limit=limit)
        if file is None:
            raise InvalidRequest("Thiếu tệp tải lên.")
        with c.upload_guard.slot():
            up = validate_upload(file.file, file.filename, limit)
            doc = c.documents.upload(up, request_id_var.get())
        return JSONResponse(DocumentOut.of(doc).model_dump(mode="json"), status_code=202,
                            headers={"Location": f"/api/v1/documents/{doc.id}", **NO_STORE})

    def _uuid(doc_id: str) -> uuid.UUID:
        try:
            return uuid.UUID(doc_id)
        except ValueError:
            raise NotFound("Tài liệu không còn tồn tại.") from None

    @app.get("/api/v1/documents/{doc_id}")
    def get_document(doc_id: str):
        return JSONResponse(DocumentOut.of(c.documents.get(_uuid(doc_id))).model_dump(mode="json"), headers=NO_STORE)

    @app.delete("/api/v1/documents/{doc_id}", status_code=204)
    def delete_document(doc_id: str):
        c.documents.delete(_uuid(doc_id), request_id_var.get())
        return Response(status_code=204)

    @app.get("/api/v1/documents/{doc_id}/file")
    def get_document_file(doc_id: str, request: Request):
        did = _uuid(doc_id)
        doc = c.documents.get(did)
        etag = f'"{doc.content_sha256}"'
        if request.headers.get("if-none-match") == etag:
            return Response(status_code=304, headers={"ETag": etag})
        size = doc.size_bytes
        rng = None
        hdr = request.headers.get("range")
        if hdr:
            m = _RANGE_RE.match(hdr.strip())
            if not m or (not m.group(1) and not m.group(2)):
                return _range_error(size)
            if m.group(1):
                start, end = int(m.group(1)), int(m.group(2)) if m.group(2) else size - 1
            else:
                start, end = max(0, size - int(m.group(2))), size - 1
            if start >= size or start > end:
                return _range_error(size)
            rng = (start, min(end, size - 1))
        _, real_size, body = c.documents.open_file(did, rng)
        headers = {
            "Content-Disposition": f"inline; filename*=UTF-8''{quote(doc.name)}",
            "X-Content-Type-Options": "nosniff", "Accept-Ranges": "bytes", "ETag": etag,
            "Cache-Control": "private, max-age=0, must-revalidate",
        }
        if rng:
            headers["Content-Range"] = f"bytes {rng[0]}-{rng[1]}/{real_size}"
            headers["Content-Length"] = str(rng[1] - rng[0] + 1)
            return StreamingResponse(body, status_code=206, media_type="application/pdf", headers=headers)
        headers["Content-Length"] = str(real_size)
        return StreamingResponse(body, media_type="application/pdf", headers=headers)

    @app.post("/api/v1/questions")
    def ask_question(body: QuestionIn):
        q = body.question.strip()
        if not q:
            raise EmptyQuestion("Vui lòng nhập câu hỏi.")
        if s.max_question_length is not None and len(q) > s.max_question_length:
            raise QuestionTooLong(f"Câu hỏi dài hơn {s.max_question_length} ký tự.", limit=s.max_question_length)
        with c.question_guard.slot():
            result = c.answers.ask(q)
        return JSONResponse(AnswerOut.of(result).model_dump(mode="json"), headers=NO_STORE)

    @app.api_route("/api/{rest:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    def api_not_found(rest: str):
        raise NotFound("Không tìm thấy.")

    # ---------------- giao diện web đã build (demo một cổng; sản xuất dùng proxy S8-06)
    dist = Path(s.web_dist)
    if dist.is_dir():
        @app.get("/{path:path}", include_in_schema=False)
        def spa(path: str):
            f = (dist / path).resolve()
            if path and f.is_file() and dist.resolve() in f.parents:
                return FileResponse(f)
            return FileResponse(dist / "index.html", headers={"Cache-Control": "no-cache"})

    return app
