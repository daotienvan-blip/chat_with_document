"""Kiểm thử tích hợp trên PostgreSQL thật: lược đồ, tải lên, hàng đợi, xử lý, hỏi đáp, nguồn, xóa, đối soát.

Mọi phản hồi API đi qua assert_matches_openapi (S1-03/S8-03).
"""
from __future__ import annotations

import threading
import time
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from cwd_server.core.errors import AiUnavailable, StorageUnavailable
from cwd_server.core.types import FailureReason, JobType
from tests.conftest import upload
from tests.fixtures import pdfs
from tests.support.openapi_assert import assert_matches_openapi

pytestmark = pytest.mark.integration

CONTRACT = [  # ba hợp đồng nhỏ dùng nhiều lần
    "Hợp đồng A. Điều khoản thanh toán: bên mua thanh toán trong vòng 30 ngày kể từ ngày nhận hóa đơn. "
    "Phí phạt chậm thanh toán là 0,05% mỗi ngày.",
    "Phụ lục. Thời hạn giao hàng là 15 ngày làm việc sau khi ký hợp đồng.",
]


def _ready(client, runner, data, name="hop-dong-A.pdf"):
    r = upload(client, data, name)
    assert r.status_code == 202, r.text
    runner.run_until_idle()
    doc = client.get(f"/api/v1/documents/{r.json()['id']}").json()
    return doc


def _cite_all(system, user):  # LLM giả: trích dẫn mọi đoạn đã gửi
    import re
    ids = re.findall(r'<doan id="(c\d+)"', user)
    return {"status": "answered", "answer": "Câu trả lời tổng hợp.", "citations": ids}


# ------------------------------------------------------------------ S0-04 ràng buộc lược đồ
def test_schema_constraints(container):
    ok = dict(id=uuid.uuid4(), name="a.pdf", size=1, key=f"documents/{uuid.uuid4()}.pdf", sha="a" * 64)
    ins = ("INSERT INTO documents (id,name,size_bytes,storage_key,content_sha256,status,failure_reason,ready_at) "
           "VALUES (:id,:name,:size,:key,:sha,:st,:fr,:ra)")
    bad = [dict(st="failed", fr=None, ra=None), dict(st="processing", fr="FILE_CORRUPT", ra=None),
           dict(st="ready", fr=None, ra=None), dict(st="weird", fr=None, ra=None),
           dict(st="processing", fr=None, ra=None, key="../x.pdf"), dict(st="processing", fr=None, ra=None, size=0),
           dict(st="processing", fr=None, ra=None, sha="xyz")]
    for b in bad:
        with pytest.raises(IntegrityError), container.db.tx() as c:
            c.execute(text(ins), {**ok, "id": uuid.uuid4(), **b})
    with container.db.tx() as c:
        c.execute(text(ins), {**ok, "st": "processing", "fr": None, "ra": None})
        c.execute(text("INSERT INTO chunks (document_id,chunk_index,page_start,page_end,text,embedding) "
                       "VALUES (:d,0,1,1,'x', CAST(:v AS vector))"), dict(d=ok["id"], v=str([0.0] * 64)))
    with pytest.raises(IntegrityError), container.db.tx() as c:  # page_start > page_end
        c.execute(text("INSERT INTO chunks (document_id,chunk_index,page_start,page_end,text,embedding) "
                       "VALUES (:d,1,3,2,'x', CAST(:v AS vector))"), dict(d=ok["id"], v=str([0.0] * 64)))
    with pytest.raises(IntegrityError), container.db.tx() as c:  # trùng chỉ số đoạn
        c.execute(text("INSERT INTO chunks (document_id,chunk_index,page_start,page_end,text,embedding) "
                       "VALUES (:d,0,1,1,'y', CAST(:v AS vector))"), dict(d=ok["id"], v=str([0.0] * 64)))
    with container.db.tx() as c:  # việc hoạt động trùng bị bỏ qua (jobs_active_uq)
        container.jobs.enqueue(c, JobType.PROCESS_DOCUMENT, ok["id"])
        container.jobs.enqueue(c, JobType.PROCESS_DOCUMENT, ok["id"])
        assert c.execute(text("SELECT count(*) FROM jobs")).scalar_one() == 1
        c.execute(text("DELETE FROM documents WHERE id=:id"), dict(id=ok["id"]))
        assert c.execute(text("SELECT count(*) FROM chunks")).scalar_one() == 0  # cascade


# ------------------------------------------------------------------ S1: tải lên & danh sách
@pytest.mark.req("US-001-AC1")
@pytest.mark.req("US-004-AC1")
def test_upload_list_get(client, store):
    r = upload(client, pdfs.text_pdf(CONTRACT), "hợp đồng A.pdf")
    assert_matches_openapi(r)
    body = r.json()
    assert body["status"] == "processing" and r.headers["location"] == f"/api/v1/documents/{body['id']}"
    upload(client, pdfs.text_pdf(["Tài liệu thứ hai"]), "b.pdf")
    lst = client.get("/api/v1/documents")
    assert_matches_openapi(lst)
    assert lst.json()["total"] == 2 and lst.json()["items"][0]["name"] == "b.pdf"  # mới nhất trước
    assert {"storage_key", "content_sha256", "deleted_at"}.isdisjoint(lst.json()["items"][0])
    one = client.get(f"/api/v1/documents/{body['id']}")
    assert_matches_openapi(one)
    assert one.json()["name"] == "hợp đồng A.pdf"
    assert len(list(store.list_keys("documents/"))) == 2


@pytest.mark.req("US-001-AC2")
@pytest.mark.req("US-001-AC3")
def test_upload_rejections(client, container):
    container.settings.max_file_size_mb = 1
    big = upload(client, b"%PDF-" + b"a" * (1024 * 1024 + 10), "lon.pdf")
    assert_matches_openapi(big)
    assert big.status_code == 413 and big.json()["code"] == "FILE_TOO_LARGE" and big.json()["limit"] == 1
    docx = upload(client, b"PK\x03\x04 word", "bao-cao.docx")
    assert docx.status_code == 400 and docx.json()["code"] == "UNSUPPORTED_TYPE"
    assert_matches_openapi(docx)
    missing = client.post("/api/v1/documents", data={"x": "1"})
    assert missing.status_code == 400 and missing.json()["code"] == "INVALID_REQUEST"
    assert client.get("/api/v1/documents").json()["total"] == 0  # không tạo bản ghi


@pytest.mark.req("US-003-AC4")
def test_upload_atomic_on_failures(client, container, store, monkeypatch):
    store.fail_next = StorageUnavailable()
    r = upload(client, pdfs.text_pdf(["x"]), "a.pdf")
    assert r.status_code == 503 and r.json()["code"] == "STORAGE_UNAVAILABLE" and "retry-after" in r.headers

    def boom(*a, **k):
        raise RuntimeError("db down")
    monkeypatch.setattr(container.docs, "add", boom)
    r = upload(client, pdfs.text_pdf(["x"]), "a.pdf")
    assert r.status_code == 500 and r.json()["code"] == "INTERNAL_ERROR" and r.json()["requestId"]
    assert "RuntimeError" not in r.text and "Traceback" not in r.text
    monkeypatch.undo()
    assert list(store.list_keys("documents/")) == []  # bù trừ: không có tệp mồ côi
    with container.db.read() as c:
        assert c.execute(text("SELECT count(*) FROM documents")).scalar_one() == 0
        assert c.execute(text("SELECT count(*) FROM jobs")).scalar_one() == 0


# ------------------------------------------------------------------ S2: hàng đợi & xử lý
def test_job_queue_concurrency_and_backoff(container):
    ids = [uuid.uuid4() for _ in range(20)]
    with container.db.tx() as c:
        for d in ids:
            container.jobs.enqueue(c, JobType.PROCESS_DOCUMENT, d)
    claimed, lock = [], threading.Lock()

    def worker():
        while True:
            with container.db.tx() as c:
                j = container.jobs.claim(c)
            if not j:
                return
            with lock:
                claimed.append(j.id)
    ts = [threading.Thread(target=worker) for _ in range(5)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    assert len(claimed) == 20 and len(set(claimed)) == 20  # mỗi việc nhận đúng một lần
    with container.db.tx() as c:  # quá hạn khóa ⇒ quay về hàng đợi
        c.execute(text("UPDATE jobs SET locked_until = now() - interval '1 minute'"))
        assert container.jobs.release_overdue(c) == 20
        j = container.jobs.claim(c)
        container.jobs.fail(c, j.id, "x", run_after=datetime.now(UTC) - timedelta(seconds=1), count_attempt=False)
        att = c.execute(text("SELECT attempts FROM jobs WHERE id=:i"), dict(i=j.id)).scalar_one()
    assert att == 1  # count_attempt=False hoàn lại lần thử đã cộng lúc claim


@pytest.mark.req("US-002-AC1")
@pytest.mark.req("US-003-AC1")
@pytest.mark.req("US-003-AC2")
@pytest.mark.req("US-003-AC3")
@pytest.mark.parametrize("data,status,reason", [
    (pdfs.text_pdf(CONTRACT), "ready", None),
    (pdfs.corrupt_pdf(), "failed", "FILE_CORRUPT"),
    (pdfs.encrypted_pdf(), "failed", "FILE_ENCRYPTED"),
    (pdfs.image_only_pdf(), "failed", "NO_EXTRACTABLE_TEXT"),
], ids=["ready", "corrupt", "encrypted", "image-only"])
def test_ingestion_outcomes(client, runner, container, data, status, reason):
    doc = _ready(client, runner, data)
    assert doc["status"] == status and doc["failureReason"] == reason
    with container.db.read() as c:
        n = container.chunks.count_for(c, uuid.UUID(doc["id"]))
    assert (n > 0) == (status == "ready")
    if status == "ready":
        assert doc["pageCount"] == 2


def test_ingestion_idempotent_and_deleted_midway(client, runner, container):
    doc = _ready(client, runner, pdfs.text_pdf(CONTRACT))
    did = uuid.UUID(doc["id"])
    with container.db.read() as c:
        n1 = container.chunks.count_for(c, did)
    container.ingestion.process(did)  # chạy lại
    with container.db.read() as c:
        assert container.chunks.count_for(c, did) == n1
    # xóa mềm trong lúc xử lý ⇒ không ghi đoạn
    r = upload(client, pdfs.text_pdf(CONTRACT), "b.pdf")
    d2 = uuid.UUID(r.json()["id"])
    orig = container.docs.lock_for_update

    def delete_then_lock(c, doc_id):
        with container.db.tx() as c2:
            container.docs.mark_deleted(c2, doc_id)
        return orig(c, doc_id)
    container.docs.lock_for_update = delete_then_lock
    try:
        runner.run_until_idle()
    finally:
        container.docs.lock_for_update = orig
    with container.db.read() as c:
        assert container.chunks.count_for(c, d2) == 0


def test_ingestion_ai_retry_then_terminal(client, runner, container, fake_llm):
    fake_llm.embed_error = AiUnavailable()
    container.llm.embed_retries = 0
    r = upload(client, pdfs.text_pdf(CONTRACT))
    did = r.json()["id"]
    for _ in range(3):
        runner.run_until_idle()
        with container.db.tx() as c:
            c.execute(text("UPDATE jobs SET run_after = now() WHERE status='queued'"))
        container.llm.breaker.success()  # không để breaker ảnh hưởng đếm lần thử trong test này
    doc = client.get(f"/api/v1/documents/{did}").json()
    assert doc["status"] == "failed" and doc["failureReason"] == "PROCESSING_ERROR"
    fake_llm.embed_error = None  # lần sau thành công (tài liệu mới)
    assert _ready(client, runner, pdfs.text_pdf(CONTRACT), "c.pdf")["status"] == "ready"


# ------------------------------------------------------------------ S3–S5: hỏi đáp
@pytest.mark.req("US-006-AC1")
@pytest.mark.req("US-007-AC1")
@pytest.mark.req("US-002-AC2")
def test_ask_answered_with_sources(client, runner, fake_llm):
    doc = _ready(client, runner, pdfs.text_pdf(CONTRACT), "hop-dong-A.pdf")
    upload(client, pdfs.text_pdf(["Điều khoản thanh toán của tài liệu chưa xử lý"]), "dang-xu-ly.pdf")
    fake_llm.script = [_cite_all]
    r = client.post("/api/v1/questions", json={"question": "Điều khoản thanh toán là gì?"})
    assert_matches_openapi(r)
    body = r.json()
    assert body["status"] == "answered"
    assert [s["documentName"] for s in body["sources"]] == ["hop-dong-A.pdf"]  # không có tài liệu processing
    assert body["sources"][0]["documentId"] == doc["id"] and body["sources"][0]["pages"]
    assert "dang-xu-ly" not in fake_llm.last_user


@pytest.mark.req("US-010-AC1")
def test_not_found_paths(client, runner, fake_llm):
    r = client.post("/api/v1/questions", json={"question": "Có gì không?"})  # kho trống ⇒ G-L1
    assert r.json() == {"status": "not_found", "answer": "Không tìm thấy thông tin trong các tài liệu đã tải.",
                        "sources": []}
    assert fake_llm.generate_calls == 0  # không gọi LLM khi không có căn cứ
    _ready(client, runner, pdfs.text_pdf(CONTRACT))
    fake_llm.script = [{"status": "answered", "answer": "Bịa, theo hop-dong-Z.pdf", "citations": ["c99"]}]
    r = client.post("/api/v1/questions", json={"question": "Giá cổ phiếu?"})
    assert_matches_openapi(r)
    assert r.json()["status"] == "not_found" and r.json()["sources"] == []  # G-L2 hạ cấp
    fake_llm.script = ["không phải dict"]
    r = client.post("/api/v1/questions", json={"question": "x?"})
    assert r.json()["status"] == "not_found"  # đầu ra sai schema hai lần ⇒ not_found


@pytest.mark.req("US-007-AC2")
@pytest.mark.req("US-009-AC1")
def test_multi_doc_sources(client, runner, fake_llm, container):
    _ready(client, runner, pdfs.text_pdf([CONTRACT[0]]), "hop-dong-A.pdf")
    _ready(client, runner, pdfs.text_pdf(["Báo giá B. Điều khoản thanh toán: trả trước 50% khi đặt hàng."]),
           "bao-gia-B.pdf")
    _ready(client, runner, pdfs.text_pdf(["Quy định nội bộ về nghỉ phép năm."]), "quy-dinh-C.pdf")

    def cite_payment(system, user):
        import re
        ids = [cid for cid, body in re.findall(r'<doan id="(c\d+)"[^>]*>\n(.*?)\n</doan>', user, re.S)
               if "thanh toán" in body]
        return {"status": "answered", "answer": "A: 30 ngày; B: trả trước 50% — hai tài liệu khác nhau.",
                "citations": ids}
    fake_llm.script = [cite_payment]
    r = client.post("/api/v1/questions", json={"question": "So sánh điều khoản thanh toán A và B"})
    names = sorted(s["documentName"] for s in r.json()["sources"])
    assert names == ["bao-gia-B.pdf", "hop-dong-A.pdf"]  # đủ hai, không thừa quy-dinh-C
    assert len(fake_llm.last_user.split("<doan ")) - 1 <= container.settings.rag_context_chunks


@pytest.mark.req("US-010-AC2")
def test_partial_requires_sources(client, runner, fake_llm):
    _ready(client, runner, pdfs.text_pdf(CONTRACT))
    fake_llm.script = [{"status": "partial", "answer": "Phạt 0,05%/ngày; bảo hành không tìm thấy.",
                        "citations": ["c1"]}]
    r = client.post("/api/v1/questions", json={"question": "Phí phạt và bảo hành?"})
    assert r.json()["status"] == "partial" and len(r.json()["sources"]) == 1
    fake_llm.script = [{"status": "partial", "answer": "x", "citations": []}]
    assert client.post("/api/v1/questions", json={"question": "Phí phạt?"}).json()["status"] == "not_found"


def test_question_validation(client, container):
    r = client.post("/api/v1/questions", json={"question": "   "})
    assert r.status_code == 400 and r.json()["code"] == "EMPTY_QUESTION"
    assert_matches_openapi(r)
    container.settings.max_question_length = 10
    r = client.post("/api/v1/questions", json={"question": "x" * 11})
    assert r.json()["code"] == "QUESTION_TOO_LONG" and r.json()["limit"] == 10
    r = client.post("/api/v1/questions", json={"question": "x", "extra": 1})
    assert r.json()["code"] == "INVALID_REQUEST"


def test_ai_errors_mapped(client, runner, fake_llm, container):
    _ready(client, runner, pdfs.text_pdf(CONTRACT))
    container.llm.generate_retries = 0
    from cwd_server.core.errors import AiTimeout
    fake_llm.script = [AiTimeout()]
    r = client.post("/api/v1/questions", json={"question": "Điều khoản thanh toán?"})
    assert r.status_code == 504 and r.json()["code"] == "AI_TIMEOUT"
    assert_matches_openapi(r)
    fake_llm.script = [AiUnavailable()]
    r = client.post("/api/v1/questions", json={"question": "Điều khoản thanh toán?"})
    assert r.status_code == 502 and r.json()["code"] == "AI_UNAVAILABLE"
    assert client.get("/api/v1/documents").status_code == 200  # phần khác vẫn chạy


# ------------------------------------------------------------------ S4: trang và tệp
@pytest.mark.req("US-008-AC1")
def test_source_pages_match(client, runner, fake_llm):
    _ready(client, runner, pdfs.token_pages_pdf(6), "token.pdf")

    def cite_token(token):
        def f(system, user):
            import re
            ids = [cid for cid, body in re.findall(r'<doan id="(c\d+)"[^>]*>\n(.*?)\n</doan>', user, re.S)
                   if token in body]
            return {"status": "answered", "answer": token, "citations": ids[:1]}
        return f
    for k in range(1, 7):
        fake_llm.script = [cite_token(f"ZXQ{k}")]
        r = client.post("/api/v1/questions", json={"question": f"Mã ZXQ{k} ở đâu?"}).json()
        pages = r["sources"][0]["pages"]
        assert k in pages and pages == sorted(set(pages)) and min(pages) >= 1


def test_file_endpoint(client, runner):
    data = pdfs.text_pdf(CONTRACT)
    doc = _ready(client, runner, data, "Hợp đồng A.pdf")
    url = f"/api/v1/documents/{doc['id']}/file"
    r = client.get(url)
    assert_matches_openapi(r)
    assert r.content == data and r.headers["content-type"] == "application/pdf"
    assert "filename*=UTF-8''H%E1%BB%A3p" in r.headers["content-disposition"]
    assert r.headers["accept-ranges"] == "bytes" and r.headers["etag"]
    p = client.get(url, headers={"Range": "bytes=0-9"})
    assert p.status_code == 206 and p.content == data[:10]
    assert p.headers["content-range"] == f"bytes 0-9/{len(data)}"
    assert client.get(url, headers={"Range": "bytes=-5"}).content == data[-5:]
    bad = client.get(url, headers={"Range": f"bytes={len(data) + 5}-"})
    assert bad.status_code == 416
    assert_matches_openapi(bad)
    nm = client.get(url, headers={"If-None-Match": r.headers["etag"]})
    assert nm.status_code == 304
    assert_matches_openapi(nm)


# ------------------------------------------------------------------ S6: xóa
@pytest.mark.req("US-005-AC1")
@pytest.mark.req("US-005-AC2")
def test_delete_is_immediate_everywhere(client, runner, fake_llm, container, store):
    doc = _ready(client, runner, pdfs.text_pdf(CONTRACT), "hop-dong-A.pdf")
    did = doc["id"]
    r = client.delete(f"/api/v1/documents/{did}")
    assert r.status_code == 204
    assert_matches_openapi(r)
    assert client.delete(f"/api/v1/documents/{did}").status_code == 204  # lặp lại vẫn 204
    with container.db.read() as c:
        assert c.execute(text("SELECT count(*) FROM jobs WHERE type='purge_document'")).scalar_one() == 1
    assert client.get("/api/v1/documents").json()["total"] == 0
    for u in (f"/api/v1/documents/{did}", f"/api/v1/documents/{did}/file"):
        nf = client.get(u)
        assert nf.status_code == 404 and nf.json()["code"] == "NOT_FOUND"
    fake_llm.script = [_cite_all]
    r = client.post("/api/v1/questions", json={"question": "Điều khoản thanh toán?"}).json()
    assert r["status"] == "not_found" and r["sources"] == []
    assert client.delete(f"/api/v1/documents/{uuid.uuid4()}").status_code == 404


def test_purge_order_and_race(client, runner, container, store):
    container.documents.purge_delay_s = 0
    doc = _ready(client, runner, pdfs.text_pdf(CONTRACT))
    did = uuid.UUID(doc["id"])
    client.delete(f"/api/v1/documents/{did}")
    time.sleep(0.05)
    store.fail_next = StorageUnavailable()  # bước xóa tệp lỗi ⇒ thử lại
    runner.run_until_idle()
    with container.db.read() as c:
        assert container.docs.get_any(c, did) is not None
    with container.db.tx() as c:
        c.execute(text("UPDATE jobs SET run_after = now() WHERE status='queued'"))
    runner.run_until_idle()
    with container.db.read() as c:
        assert container.docs.get_any(c, did) is None
        assert c.execute(text("SELECT count(*) FROM chunks")).scalar_one() == 0
    assert list(store.list_keys("documents/")) == []
    assert client.delete(f"/api/v1/documents/{did}").status_code == 404  # đã purge
    container.ingestion.process(did)  # việc xử lý cho tài liệu đã purge: kết thúc êm


def test_race_deleted_between_retrieve_and_sources(client, runner, fake_llm, container):
    doc = _ready(client, runner, pdfs.text_pdf(CONTRACT))

    def delete_during_generate(system, user):
        with container.db.tx() as c:
            container.docs.mark_deleted(c, uuid.UUID(doc["id"]))
        return _cite_all(system, user)
    fake_llm.script = [delete_during_generate]
    r = client.post("/api/v1/questions", json={"question": "Điều khoản thanh toán?"}).json()
    assert r["status"] == "not_found" and r["sources"] == []


# ------------------------------------------------------------------ S7/S8: guard, đối soát, quan sát
def test_busy_and_rate_limit(client, container):
    container.question_guard._sem.acquire()
    container.question_guard.wait_s = 0.01
    for _ in range(container.settings.load_max_concurrent_questions - 1):
        container.question_guard._sem.acquire()
    r = client.post("/api/v1/questions", json={"question": "x?"})
    assert r.status_code == 503 and r.json()["code"] == "SYSTEM_BUSY" and r.headers["retry-after"]
    assert_matches_openapi(r)
    container.settings.rate_limit_enabled = True
    container.rate_limiter.limits["other"] = 2
    codes = [client.get("/api/v1/documents").status_code for _ in range(4)]
    assert codes[:2] == [200, 200] and codes[-1] == 429


def test_reconcile(container, store, client, runner):
    import io
    orphan = f"documents/{uuid.uuid4()}.pdf"
    store.put(orphan, io.BytesIO(b"%PDF-x"), 6)
    store._data[orphan] = (store._data[orphan][0], time.time() - 2 * 86400)
    fresh = f"documents/{uuid.uuid4()}.pdf"
    store.put(fresh, io.BytesIO(b"%PDF-y"), 6)
    doc = _ready(client, runner, pdfs.text_pdf(CONTRACT))
    store.delete(f"documents/{doc['id']}.pdf")
    from cwd_server.worker.maintenance import Maintenance
    m = Maintenance(container.db, container.docs, container.jobs, store)
    stats = m.reconcile()
    assert stats["orphans_deleted"] == 1 and stats["missing_files"] == 1
    assert fresh in dict(store.list_keys("documents/"))
    assert m.reconcile() == {"orphans_deleted": 0, "missing_files": 0, "requeued": 0}  # idempotent
    assert client.get(f"/api/v1/documents/{doc['id']}").json()["failureReason"] == FailureReason.PROCESSING_ERROR


def test_observability_no_content_leak(client, runner, fake_llm, capsys, caplog):
    import logging
    caplog.set_level(logging.DEBUG)
    canary = "CANARYxyz123"
    _ready(client, runner, pdfs.text_pdf([f"Nội dung {canary} bí mật"]), f"{canary}.pdf")
    fake_llm.script = [_cite_all]
    client.post("/api/v1/questions", json={"question": f"Hỏi về {canary}?"})
    metrics = client.get("/metrics").text
    out = capsys.readouterr()
    assert canary not in caplog.text and canary not in out.out and canary not in out.err and canary not in metrics
    assert "cwd_answers_total" in metrics and "cwd_http_requests_total" in metrics
    assert client.get("/readyz").text == "ok" and client.get("/healthz").status_code == 200
    assert client.get("/api/v1/config").headers["x-request-id"]
