"""Xóa vật lý (S6-02), quét tồn đọng (S2-05) và đối soát kho ↔ CSDL (S7-04)."""
from __future__ import annotations

import logging
import time

from cwd_server.core.errors import RetryableError, StorageUnavailable
from cwd_server.core.types import FailureReason, Job, JobType
from cwd_server.platform import metrics

log = logging.getLogger("cwd.worker")


class Maintenance:
    def __init__(self, db, docs, jobs, store, orphan_age_s: int = 86400):
        self.db, self.docs, self.jobs, self.store = db, docs, jobs, store
        self.orphan_age_s = orphan_age_s

    def purge(self, job: Job) -> None:
        """Thứ tự: xóa tệp trước (idempotent) rồi mới xóa bản ghi — tránh tệp mồ côi (Database_Design §3.4.4)."""
        with self.db.read() as c:
            doc = self.docs.get_any(c, job.document_id)
        if doc is None:
            return
        if doc.deleted_at is None:
            return  # không xóa tài liệu chưa bị xóa mềm
        try:
            self.store.delete(doc.storage_key)
        except (StorageUnavailable, OSError) as e:
            raise RetryableError("không xóa được tệp") from e
        with self.db.tx() as c:
            self.docs.delete_row(c, job.document_id)  # cascade chunks
        log.info("đã xóa vật lý", extra={"event": "document_purged", "documentId": str(job.document_id)})

    def sweep(self) -> None:
        with self.db.tx() as c:
            self.jobs.release_overdue(c)
            self.jobs.cleanup(c)
            counts, age = self.jobs.stats(c)
        for st in ("queued", "running", "done", "failed"):
            metrics.JOBS.labels(st).set(counts.get(st, 0))
        metrics.OLDEST_JOB_AGE.set(age)

    def reconcile(self) -> dict[str, int]:
        stats = {"orphans_deleted": 0, "missing_files": 0, "requeued": 0}
        with self.db.read() as c:
            keys = self.docs.all_keys(c)
            docs = self.docs.list_visible(c)
        now = time.time()
        for key, mtime in list(self.store.list_keys("documents/")):
            if key not in keys and now - mtime > self.orphan_age_s:
                self.store.delete(key)
                stats["orphans_deleted"] += 1
        for d in docs:
            try:
                self.store.size(d.storage_key)
            except FileNotFoundError:
                if d.status.value != "failed":
                    with self.db.tx() as c:
                        self.docs.set_failed(c, d.id, FailureReason.PROCESSING_ERROR)
                    stats["missing_files"] += 1
                    log.warning("tài liệu mất tệp", extra={"event": "missing_file", "documentId": str(d.id)})
        with self.db.tx() as c:
            for doc_id in self.docs.ready_without_chunks(c):
                self.jobs.enqueue(c, JobType.PROCESS_DOCUMENT, doc_id)
                stats["requeued"] += 1
        return stats
