"""IngestionService.process (S2-04, Blueprint §3.6.1)."""
from __future__ import annotations

import logging
import time
import uuid

from cwd_server.core.errors import (
    AiTimeout,
    AiUnavailable,
    ConfigurationError,
    PdfCorrupt,
    PdfEncrypted,
    PdfTimeout,
    RetryableError,
    StorageUnavailable,
)
from cwd_server.core.ingestion.chunker import Chunker
from cwd_server.core.types import FailureReason

log = logging.getLogger("cwd.ingestion")


class IngestionService:
    def __init__(self, db, docs, chunks, store, extractor, llm, chunker: Chunker, embedding_dim: int,
                 batch_size: int = 64):
        self.db, self.docs, self.chunks, self.store = db, docs, chunks, store
        self.extractor, self.llm, self.chunker = extractor, llm, chunker
        self.dim, self.batch = embedding_dim, batch_size

    def _fail(self, doc_id: uuid.UUID, reason: FailureReason, pages: int | None = None) -> None:
        with self.db.tx() as c:
            self.docs.set_failed(c, doc_id, reason, pages)
        log.info("tài liệu lỗi", extra={"event": "document_failed", "documentId": str(doc_id), "errorCode": reason})

    def process(self, doc_id: uuid.UUID) -> None:
        t0 = time.monotonic()
        with self.db.read() as c:
            doc = self.docs.get_any(c, doc_id)
        if doc is None or doc.deleted_at is not None:
            return  # đã purge hoặc đã xóa mềm: kết thúc êm
        try:
            data = b"".join(self.store.get(doc.storage_key))
        except FileNotFoundError:
            self._fail(doc_id, FailureReason.PROCESSING_ERROR)
            return
        except (StorageUnavailable, OSError) as e:
            raise RetryableError("kho lưu trữ lỗi") from e
        try:
            pages = self.extractor.extract(data)
        except PdfEncrypted:
            return self._fail(doc_id, FailureReason.FILE_ENCRYPTED)
        except PdfCorrupt:
            return self._fail(doc_id, FailureReason.FILE_CORRUPT)
        except PdfTimeout as e:
            raise RetryableError("trích văn bản quá thời gian") from e
        drafts = self.chunker.split(pages)
        if not drafts:
            return self._fail(doc_id, FailureReason.NO_EXTRACTABLE_TEXT, len(pages))
        vectors: list[list[float]] = []
        try:
            for i in range(0, len(drafts), self.batch):
                vectors += self.llm.embed([d.text for d in drafts[i:i + self.batch]])
        except AiUnavailable as e:
            raise RetryableError("dịch vụ AI không dùng được", count_attempt=not e.breaker_open) from e
        except AiTimeout as e:
            raise RetryableError("dịch vụ AI hết thời gian") from e
        if any(len(v) != self.dim for v in vectors):
            raise ConfigurationError("số chiều embedding không khớp EMBEDDING_DIM")
        with self.db.tx() as c:
            locked = self.docs.lock_for_update(c, doc_id)
            if locked is None or locked.deleted_at is not None:
                return  # bị xóa trong lúc xử lý: không ghi đoạn (Database_Design §5.1, T3↔T4)
            self.chunks.add_batch(c, doc_id, drafts, vectors)
            self.docs.set_ready(c, doc_id, len(pages))
        log.info("tài liệu sẵn sàng", extra={"event": "document_ready", "documentId": str(doc_id),
                                            "durationMs": int((time.monotonic() - t0) * 1000),
                                            "count": len(drafts), "pages": len(pages)})
