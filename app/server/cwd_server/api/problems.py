"""Ánh xạ ProblemCode → HTTP + application/problem+json (RFC 9457), đúng openapi.yaml."""
from __future__ import annotations

import re

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from cwd_server.core.errors import DomainError
from cwd_server.platform.logging import request_id_var

PROBLEMS: dict[str, tuple[int, str, str]] = {
    "INVALID_REQUEST": (400, "Yêu cầu không hợp lệ", "Yêu cầu không hợp lệ. Vui lòng thử lại."),
    "UNSUPPORTED_TYPE": (400, "Chỉ hỗ trợ tệp PDF", "Chỉ hỗ trợ tệp PDF."),
    "FILE_TOO_LARGE": (413, "Tệp quá lớn", "Tệp lớn hơn giới hạn cho phép."),
    "EMPTY_QUESTION": (400, "Câu hỏi rỗng", "Vui lòng nhập câu hỏi."),
    "QUESTION_TOO_LONG": (400, "Câu hỏi quá dài", "Câu hỏi quá dài."),
    "NOT_FOUND": (404, "Không tìm thấy", "Tài liệu không còn tồn tại."),
    "RATE_LIMITED": (429, "Thao tác quá nhanh", "Bạn thao tác quá nhanh. Vui lòng thử lại sau ít giây."),
    "SYSTEM_BUSY": (503, "Hệ thống đang bận", "Hệ thống đang bận. Tài liệu của bạn không bị mất. Vui lòng thử lại."),
    "STORAGE_UNAVAILABLE": (503, "Chưa lưu được tệp", "Chưa lưu được tệp. Vui lòng thử lại."),
    "AI_UNAVAILABLE": (502, "Dịch vụ AI không dùng được",
                       "Dịch vụ AI tạm thời không dùng được. Câu hỏi của bạn vẫn được giữ."),
    "AI_TIMEOUT": (504, "Hết thời gian chờ", "Hết thời gian chờ. Câu hỏi của bạn vẫn được giữ."),
    "INTERNAL_ERROR": (500, "Đã xảy ra lỗi", "Đã xảy ra lỗi. Vui lòng thử lại; nếu còn lặp lại, hãy báo mã tham chiếu."),
}
RETRY_AFTER_DEFAULT = {"SYSTEM_BUSY": 5, "STORAGE_UNAVAILABLE": 5, "AI_UNAVAILABLE": 10, "RATE_LIMITED": 5}


def problem(code: str, detail: str | None = None, *, limit: int | None = None,
            retry_after: int | None = None) -> JSONResponse:
    status, title, default = PROBLEMS[code]
    rid = request_id_var.get() or ""
    body = {"type": "urn:cwd:problem:" + re.sub(r"_", "-", code.lower()), "title": title, "status": status,
            "detail": detail or default, "code": code, "requestId": rid}
    if limit is not None:
        body["limit"] = limit
    headers = {"X-Request-Id": rid, "Cache-Control": "no-store"}
    ra = retry_after if retry_after is not None else RETRY_AFTER_DEFAULT.get(code)
    if ra is not None:
        headers["Retry-After"] = str(ra)
    return JSONResponse(body, status_code=status, headers=headers, media_type="application/problem+json")


def install(app) -> None:
    @app.exception_handler(DomainError)
    def _domain(_: Request, e: DomainError):
        return problem(e.code, e.detail, limit=e.limit, retry_after=e.retry_after)

    @app.exception_handler(RequestValidationError)
    def _validation(_: Request, e: RequestValidationError):
        return problem("INVALID_REQUEST")

    @app.exception_handler(StarletteHTTPException)
    def _http(_: Request, e: StarletteHTTPException):
        if e.status_code == 404:
            return problem("NOT_FOUND", "Không tìm thấy.")
        if e.status_code == 413:
            return problem("FILE_TOO_LARGE")
        return problem("INVALID_REQUEST")

    @app.exception_handler(Exception)
    def _unexpected(_: Request, e: Exception):  # không lộ stack, đường dẫn, SQL
        import logging
        logging.getLogger("cwd.api").error("lỗi không lường trước", exc_info=e, extra={"event": "unhandled"})
        return problem("INTERNAL_ERROR")
