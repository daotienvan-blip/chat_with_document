"""DocumentService (S1-02, S6-01): tải lên nguyên tử, liệt kê, xóa mềm, mở tệp."""
from __future__ import annotations

import logging
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

from cwd_server.core.documents.validate_upload import ValidatedUpload
from cwd_server.core.errors import NotFound, StorageUnavailable
from cwd_server.core.types import Document, JobType

log = logging.getLogger("cwd.documents")


class DocumentService:
    def __init__(self, db, docs, jobs, store, purge_delay_s: int = 3600):
        self.db, self.docs, self.jobs, self.store = db, docs, jobs, store
        self.purge_delay_s = purge_delay_s

    def upload(self, up: ValidatedUpload, request_id: str | None = None) -> Document:
        doc_id = uuid.uuid4()
        key = f"documents/{doc_id}.pdf"
        try:
            self.store.put(key, up.file, up.size)
        except StorageUnavailable:
            raise
        except Exception as e:  # mọi lỗi kho ⇒ chưa tạo gì trong CSDL
            raise StorageUnavailable() from e
        finally:
            up.file.close()
        try:
            with self.db.tx() as c:
                doc = self.docs.add(c, doc_id=doc_id, name=up.name, size=up.size, key=key, sha256=up.sha256)
                self.jobs.enqueue(c, JobType.PROCESS_DOCUMENT, doc_id, request_id=request_id)
        except Exception:
            try:  # bù trừ: không để tệp mồ côi (S1-02); nếu thất bại, đối soát S7-04 sẽ dọn
                self.store.delete(key)
            except Exception:
                log.warning("không xóa được tệp sau khi giao dịch lỗi", extra={"event": "compensate_failed"})
            raise
        return doc

    def list(self) -> list[Document]:
        with self.db.read() as c:
            return self.docs.list_visible(c)

    def get(self, doc_id: uuid.UUID) -> Document:
        with self.db.read() as c:
            doc = self.docs.get_visible(c, doc_id)
        if not doc:
            raise NotFound("Tài liệu không còn tồn tại.")
        return doc

    def delete(self, doc_id: uuid.UUID, request_id: str | None = None) -> None:
        """Xóa mềm + xếp lịch xóa vật lý trong một giao dịch (Database_Design §5.1, T4)."""
        with self.db.tx() as c:
            res = self.docs.mark_deleted(c, doc_id)
            if res == "absent":
                raise NotFound("Tài liệu không còn tồn tại.")
            if res == "deleted":
                self.jobs.enqueue(c, JobType.PURGE_DOCUMENT, doc_id, request_id=request_id,
                                  run_after=datetime.now(UTC) + timedelta(seconds=self.purge_delay_s))

    def open_file(self, doc_id: uuid.UUID, byte_range: tuple[int, int] | None) -> tuple[Document, int, Iterator[bytes]]:
        doc = self.get(doc_id)
        try:
            size = self.store.size(doc.storage_key)
            if byte_range is not None:
                return doc, size, self.store.get(doc.storage_key, (byte_range[0], min(byte_range[1], size - 1)))
            return doc, size, self.store.get(doc.storage_key)
        except FileNotFoundError as e:
            raise NotFound("Tài liệu không còn tồn tại.") from e
        except StorageUnavailable:
            raise
        except OSError as e:
            raise StorageUnavailable() from e
