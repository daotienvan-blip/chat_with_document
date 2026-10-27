"""Truy cập CSDL bằng SQL tham số hóa (Database_Design §3.4.2). Mọi truy vấn đọc `chunks` đều lọc searchable."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from sqlalchemy import Connection, text

from cwd_server.core.types import (
    ChunkDraft,
    Document,
    DocumentStatus,
    FailureReason,
    Job,
    JobType,
    RetrievedChunk,
)
from cwd_server.persistence.db import to_vector_literal

SEARCHABLE = "d.status = 'ready' AND d.deleted_at IS NULL"
_DOC_COLS = "id, name, size_bytes, page_count, storage_key, content_sha256, status, failure_reason, created_at, deleted_at"


def _doc(row) -> Document:
    return Document(
        id=row.id, name=row.name, size_bytes=row.size_bytes, page_count=row.page_count,
        storage_key=row.storage_key, content_sha256=row.content_sha256.strip(),
        status=DocumentStatus(row.status),
        failure_reason=FailureReason(row.failure_reason) if row.failure_reason else None,
        created_at=row.created_at, deleted_at=row.deleted_at,
    )


class DocumentRepository:
    def add(self, c: Connection, *, doc_id: uuid.UUID, name: str, size: int, key: str, sha256: str) -> Document:
        row = c.execute(text(
            f"INSERT INTO documents (id, name, size_bytes, storage_key, content_sha256, status) "
            f"VALUES (:id, :name, :size, :key, :sha, 'processing') RETURNING {_DOC_COLS}"),
            dict(id=doc_id, name=name, size=size, key=key, sha=sha256)).one()
        return _doc(row)

    def get_visible(self, c: Connection, doc_id: uuid.UUID) -> Document | None:
        row = c.execute(text(f"SELECT {_DOC_COLS} FROM documents WHERE id = :id AND deleted_at IS NULL"),
                        dict(id=doc_id)).one_or_none()
        return _doc(row) if row else None

    def get_any(self, c: Connection, doc_id: uuid.UUID) -> Document | None:
        row = c.execute(text(f"SELECT {_DOC_COLS} FROM documents WHERE id = :id"), dict(id=doc_id)).one_or_none()
        return _doc(row) if row else None

    def list_visible(self, c: Connection) -> list[Document]:
        rows = c.execute(text(
            f"SELECT {_DOC_COLS} FROM documents WHERE deleted_at IS NULL ORDER BY created_at DESC, id")).all()
        return [_doc(r) for r in rows]

    def lock_for_update(self, c: Connection, doc_id: uuid.UUID) -> Document | None:
        row = c.execute(text(f"SELECT {_DOC_COLS} FROM documents WHERE id = :id FOR UPDATE"),
                        dict(id=doc_id)).one_or_none()
        return _doc(row) if row else None

    def set_ready(self, c: Connection, doc_id: uuid.UUID, page_count: int) -> None:
        c.execute(text("UPDATE documents SET status='ready', failure_reason=NULL, page_count=:p, ready_at=now() "
                       "WHERE id=:id"), dict(id=doc_id, p=page_count))

    def set_failed(self, c: Connection, doc_id: uuid.UUID, reason: FailureReason, page_count: int | None = None) -> None:
        c.execute(text("UPDATE documents SET status='failed', failure_reason=:r, ready_at=NULL, "
                       "page_count=COALESCE(:p, page_count) WHERE id=:id AND deleted_at IS NULL"),
                  dict(id=doc_id, r=reason.value, p=page_count))

    def mark_deleted(self, c: Connection, doc_id: uuid.UUID) -> str:
        """Trả 'deleted' | 'already' | 'absent'."""
        r = c.execute(text("UPDATE documents SET deleted_at = now() WHERE id = :id AND deleted_at IS NULL"),
                      dict(id=doc_id))
        if r.rowcount:
            return "deleted"
        exists = c.execute(text("SELECT 1 FROM documents WHERE id = :id"), dict(id=doc_id)).first()
        return "already" if exists else "absent"

    def delete_row(self, c: Connection, doc_id: uuid.UUID) -> None:
        c.execute(text("DELETE FROM documents WHERE id = :id"), dict(id=doc_id))

    def all_keys(self, c: Connection) -> set[str]:
        return {r[0] for r in c.execute(text("SELECT storage_key FROM documents")).all()}

    def ready_without_chunks(self, c: Connection) -> list[uuid.UUID]:
        rows = c.execute(text(
            "SELECT d.id FROM documents d LEFT JOIN chunks c ON c.document_id = d.id "
            "WHERE d.status='ready' AND d.deleted_at IS NULL GROUP BY d.id HAVING count(c.id)=0")).all()
        return [r[0] for r in rows]


class ChunkRepository:
    def add_batch(self, c: Connection, doc_id: uuid.UUID, drafts: list[ChunkDraft], vectors: list[list[float]]) -> int:
        if not drafts:
            return 0
        c.execute(text(
            "INSERT INTO chunks (document_id, chunk_index, page_start, page_end, text, embedding) "
            "VALUES (:doc, :idx, :ps, :pe, :text, CAST(:vec AS vector)) "
            "ON CONFLICT (document_id, chunk_index) DO NOTHING"),
            [dict(doc=doc_id, idx=d.chunk_index, ps=d.page_start, pe=d.page_end, text=d.text,
                  vec=to_vector_literal(v)) for d, v in zip(drafts, vectors, strict=True)])
        return len(drafts)

    def count_for(self, c: Connection, doc_id: uuid.UUID) -> int:
        return c.execute(text("SELECT count(*) FROM chunks WHERE document_id=:d"), dict(d=doc_id)).scalar_one()

    def vector_candidates(self, c: Connection, vec: list[float], k: int, mode: str = "exact",
                          ef_search: int = 100) -> list[RetrievedChunk]:
        # Chế độ "exact": cộng 0 để trình tối ưu không dùng chỉ mục HNSW (quét chính xác, xem spike S3-00).
        order = "(c.embedding <=> CAST(:q AS vector))" + (" + 0" if mode == "exact" else "")
        if mode == "hnsw":
            c.execute(text(f"SET LOCAL hnsw.ef_search = {int(ef_search)}"))
            c.execute(text("SET LOCAL hnsw.iterative_scan = relaxed_order"))
        rows = c.execute(text(
            f"SELECT c.id, c.document_id, d.name, c.page_start, c.page_end, c.text, "
            f"1 - (c.embedding <=> CAST(:q AS vector)) AS score "
            f"FROM chunks c JOIN documents d ON d.id = c.document_id WHERE {SEARCHABLE} "
            f"ORDER BY {order} LIMIT :k"), dict(q=to_vector_literal(vec), k=k)).all()
        return [RetrievedChunk(r.id, r.document_id, r.name, r.page_start, r.page_end, r.text, 0.0, float(r.score))
                for r in rows]

    def fts_candidates(self, c: Connection, tsquery: str, k: int) -> list[RetrievedChunk]:
        if not tsquery:
            return []
        rows = c.execute(text(
            f"SELECT c.id, c.document_id, d.name, c.page_start, c.page_end, c.text, "
            f"ts_rank_cd(c.tsv, to_tsquery('simple', :q)) AS score "
            f"FROM chunks c JOIN documents d ON d.id = c.document_id "
            f"WHERE {SEARCHABLE} AND c.tsv @@ to_tsquery('simple', :q) ORDER BY score DESC, c.id LIMIT :k"),
            dict(q=tsquery, k=k)).all()
        return [RetrievedChunk(r.id, r.document_id, r.name, r.page_start, r.page_end, r.text, 0.0, None)
                for r in rows]

    def by_ids(self, c: Connection, ids: list[uuid.UUID]) -> list[RetrievedChunk]:
        if not ids:
            return []
        rows = c.execute(text(
            f"SELECT c.id, c.document_id, d.name, c.page_start, c.page_end, c.text "
            f"FROM chunks c JOIN documents d ON d.id = c.document_id "
            f"WHERE c.id = ANY(:ids) AND {SEARCHABLE}"), dict(ids=list(ids))).all()
        return [RetrievedChunk(r.id, r.document_id, r.name, r.page_start, r.page_end, r.text, 0.0, None)
                for r in rows]


class JobRepository:
    def enqueue(self, c: Connection, job_type: JobType, doc_id: uuid.UUID, *,
                run_after: datetime | None = None, request_id: str | None = None) -> None:
        c.execute(text(
            "INSERT INTO jobs (type, document_id, run_after, request_id) "
            "VALUES (:t, :d, COALESCE(:ra, now()), :rid) ON CONFLICT DO NOTHING"),
            dict(t=job_type.value, d=doc_id, ra=run_after, rid=request_id))

    def claim(self, c: Connection, lock_minutes: int = 10) -> Job | None:
        row = c.execute(text(
            "UPDATE jobs SET status='running', attempts=attempts+1, "
            "locked_until = now() + make_interval(mins => :m) "
            "WHERE id = (SELECT id FROM jobs WHERE status='queued' AND run_after <= now() "
            "ORDER BY run_after LIMIT 1 FOR UPDATE SKIP LOCKED) "
            "RETURNING id, type, document_id, attempts, request_id"), dict(m=lock_minutes)).one_or_none()
        if not row:
            return None
        return Job(row.id, JobType(row.type), row.document_id, row.attempts, row.request_id)

    def complete(self, c: Connection, job_id: uuid.UUID) -> None:
        c.execute(text("UPDATE jobs SET status='done', locked_until=NULL, finished_at=now() WHERE id=:id"),
                  dict(id=job_id))

    def fail(self, c: Connection, job_id: uuid.UUID, error: str, *, run_after: datetime | None,
             count_attempt: bool = True) -> None:
        """run_after=None ⇒ thất bại kết thúc; ngược lại xếp lại hàng đợi."""
        if run_after is None:
            c.execute(text("UPDATE jobs SET status='failed', locked_until=NULL, finished_at=now(), last_error=:e "
                           "WHERE id=:id"), dict(id=job_id, e=error[:500]))
        else:
            c.execute(text(
                "UPDATE jobs SET status='queued', locked_until=NULL, run_after=:ra, last_error=:e, "
                "attempts = attempts - CASE WHEN :count THEN 0 ELSE 1 END WHERE id=:id"),
                dict(id=job_id, ra=run_after, e=error[:500], count=count_attempt))

    def release_overdue(self, c: Connection) -> int:
        return c.execute(text("UPDATE jobs SET status='queued', locked_until=NULL "
                              "WHERE status='running' AND locked_until < now()")).rowcount

    def cleanup(self, c: Connection, older_than: timedelta = timedelta(days=7)) -> int:
        return c.execute(text("DELETE FROM jobs WHERE status IN ('done','failed') AND finished_at < now() - :age"),
                         dict(age=older_than)).rowcount

    def can_enqueue(self, c: Connection) -> bool:
        """readyz của api: cwd_api chỉ có INSERT trên jobs (Database_Design §4.1), không đọc được hàng đợi."""
        return bool(c.execute(text("SELECT has_table_privilege('jobs', 'INSERT')")).scalar_one())

    def stats(self, c: Connection) -> tuple[dict[str, int], float]:
        counts = {r[0]: r[1] for r in c.execute(text("SELECT status, count(*) FROM jobs GROUP BY status")).all()}
        age = c.execute(text("SELECT COALESCE(EXTRACT(EPOCH FROM now() - min(run_after)), 0) FROM jobs "
                             "WHERE status='queued' AND run_after <= now()")).scalar_one()
        return counts, float(age)
