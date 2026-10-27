"""S8-02: vai trò cwd_api / cwd_worker chỉ có quyền tối thiểu (Database_Design §4.1).

Tạo hai vai trò đăng nhập tạm thời thuộc nhóm, chạy các truy vấn thật bằng đúng vai trò và kiểm tra thao tác bị cấm.
"""
from __future__ import annotations

import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

from tests.conftest import TEST_DB

pytestmark = pytest.mark.integration
PW = "test-only-" + uuid.uuid4().hex[:8]


@pytest.fixture(scope="module")
def roles(_schema):
    admin = create_engine(TEST_DB)
    with admin.begin() as c:
        for login, group in (("cwd_api_login", "cwd_api"), ("cwd_worker_login", "cwd_worker")):
            c.execute(text(f"DROP ROLE IF EXISTS {login}"))
            c.execute(text(f"CREATE ROLE {login} LOGIN PASSWORD '{PW}' IN ROLE {group}"))
        c.execute(text("ALTER ROLE cwd_api_login SET statement_timeout = '30s'"))
    base = admin.url
    engines = {r: create_engine(base.set(username=f"{r}_login", password=PW, host="localhost")) for r in ("cwd_api", "cwd_worker")}
    yield admin, engines
    for e in engines.values():
        e.dispose()
    with admin.begin() as c:
        c.execute(text("DROP OWNED BY cwd_api_login, cwd_worker_login"))
        c.execute(text("DROP ROLE IF EXISTS cwd_api_login"))
        c.execute(text("DROP ROLE IF EXISTS cwd_worker_login"))
    admin.dispose()


def _denied(engine, sql: str, **params) -> None:
    with pytest.raises(ProgrammingError, match="permission denied"), engine.begin() as c:
        c.execute(text(sql), params)


def test_api_and_worker_privileges(clean_db, roles):
    admin, eng = roles
    api, worker = eng["cwd_api"], eng["cwd_worker"]
    did = uuid.uuid4()
    vec = str([0.0] * 64)
    # api: tạo tài liệu + xếp việc, xóa mềm, đọc để truy xuất
    with api.begin() as c:
        c.execute(text("INSERT INTO documents (id,name,size_bytes,storage_key,content_sha256,status) "
                       "VALUES (:id,'a.pdf',1,:k,:s,'processing')"),
                  dict(id=did, k=f"documents/{did}.pdf", s="a" * 64))
        c.execute(text("INSERT INTO jobs (type, document_id) VALUES ('process_document', :d)"), dict(d=did))
        assert c.execute(text("SHOW statement_timeout")).scalar_one() == "30s"
    # worker: nhận việc, khóa dòng, ghi đoạn, đặt ready, xóa vật lý
    with worker.begin() as c:
        c.execute(text("UPDATE jobs SET status='running', locked_until=now() + interval '1 minute' WHERE document_id=:d"),
                  dict(d=did))
        c.execute(text("SELECT id FROM documents WHERE id=:d FOR UPDATE"), dict(d=did))
        c.execute(text("INSERT INTO chunks (document_id,chunk_index,page_start,page_end,text,embedding) "
                       "VALUES (:d,0,1,1,'x',CAST(:v AS vector))"), dict(d=did, v=vec))
        c.execute(text("UPDATE documents SET status='ready', ready_at=now(), page_count=1 WHERE id=:d"), dict(d=did))
    with api.begin() as c:
        assert c.execute(text("SELECT count(*) FROM chunks c JOIN documents d ON d.id=c.document_id "
                              "WHERE d.status='ready' AND d.deleted_at IS NULL")).scalar_one() == 1
        c.execute(text("UPDATE documents SET deleted_at=now() WHERE id=:d"), dict(d=did))
    # thao tác bị cấm
    _denied(api, "INSERT INTO chunks (document_id,chunk_index,page_start,page_end,text,embedding) "
                 "VALUES (:d,1,1,1,'x',CAST(:v AS vector))", d=did, v=vec)
    _denied(api, "DELETE FROM chunks")
    _denied(api, "UPDATE chunks SET text='y'")
    _denied(api, "DELETE FROM documents WHERE id=:d", d=did)
    _denied(api, "UPDATE documents SET name='x' WHERE id=:d", d=did)
    _denied(api, "UPDATE documents SET status='ready' WHERE id=:d", d=did)
    _denied(api, "SELECT * FROM jobs")
    _denied(api, "DELETE FROM jobs")
    _denied(worker, "UPDATE documents SET deleted_at=NULL WHERE id=:d", d=did)
    _denied(worker, "UPDATE documents SET name='x' WHERE id=:d", d=did)
    _denied(worker, "CREATE TABLE evil (x int)")
    with worker.begin() as c:
        c.execute(text("DELETE FROM documents WHERE id=:d"), dict(d=did))
        assert c.execute(text("SELECT count(*) FROM chunks")).scalar_one() == 0


def test_readyz_queries_work_under_least_privilege(clean_db, roles):
    """Lỗi tìm thấy ở S8-05: /readyz từng đọc bảng jobs ⇒ luôn 503 khi api chạy bằng cwd_api."""
    from cwd_server.persistence.repositories import JobRepository

    _, eng = roles
    with eng["cwd_api"].connect() as c:
        c.execute(text("SELECT 1"))
        assert JobRepository().can_enqueue(c)
    with eng["cwd_worker"].connect() as c:
        JobRepository().stats(c)  # vòng quét của worker vẫn đọc được hàng đợi
