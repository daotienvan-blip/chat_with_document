"""Vòng xử lý việc nền (S2-03): nhận việc an toàn nhiều worker, thử lại có lịch, phân biệt lỗi kết thúc."""
from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable, Mapping
from datetime import UTC, datetime, timedelta

from cwd_server.core.errors import RetryableError
from cwd_server.core.types import FailureReason, Job, JobType
from cwd_server.platform import metrics
from cwd_server.platform.logging import request_id_var

log = logging.getLogger("cwd.worker")
MAX_ATTEMPTS = 3
BACKOFF = {1: 30, 2: 120}  # giây; lần 3 thất bại ⇒ kết thúc


def next_run_after(attempts: int, now: datetime | None = None) -> datetime | None:
    if attempts >= MAX_ATTEMPTS:
        return None
    return (now or datetime.now(UTC)) + timedelta(seconds=BACKOFF.get(attempts, 120))


class Runner:
    def __init__(self, db, jobs, docs, handlers: Mapping[JobType, Callable[[Job], object]], lock_minutes: int = 10,
                 poll_s: float = 1.0, breaker_reopen_at: Callable[[], datetime | None] | None = None):
        self.db, self.jobs, self.docs, self.handlers = db, jobs, docs, handlers
        self.lock_minutes, self.poll_s = lock_minutes, poll_s
        self.breaker_reopen_at = breaker_reopen_at or (lambda: None)
        self.stop = threading.Event()

    def run_once(self) -> bool:
        """Xử lý tối đa một việc. Trả True nếu đã nhận được việc."""
        with self.db.tx() as c:
            job = self.jobs.claim(c, self.lock_minutes)
        if job is None:
            return False
        token = request_id_var.set(job.request_id)
        t0 = time.monotonic()
        try:
            self.handlers[job.type](job)
        except RetryableError as e:
            attempts = job.attempts if e.count_attempt else job.attempts - 1
            ra = next_run_after(attempts)
            if not e.count_attempt:
                ra = self.breaker_reopen_at() or (datetime.now(UTC) + timedelta(seconds=30))
            with self.db.tx() as c:
                if ra is None:
                    self.jobs.fail(c, job.id, str(e), run_after=None)
                    if job.type == JobType.PROCESS_DOCUMENT:
                        self.docs.set_failed(c, job.document_id, FailureReason.PROCESSING_ERROR)
                else:
                    self.jobs.fail(c, job.id, str(e), run_after=ra, count_attempt=e.count_attempt)
            log.warning("việc lỗi tạm thời", extra={"event": "job_retry", "jobId": str(job.id),
                                                    "errorCode": type(e.__cause__ or e).__name__})
        except Exception as e:  # lỗi không lường trước: kết thúc việc, không lặp vô hạn
            with self.db.tx() as c:
                self.jobs.fail(c, job.id, type(e).__name__, run_after=None)
                if job.type == JobType.PROCESS_DOCUMENT:
                    self.docs.set_failed(c, job.document_id, FailureReason.PROCESSING_ERROR)
            log.exception("việc lỗi", extra={"event": "job_error", "jobId": str(job.id)})
        else:
            with self.db.tx() as c:
                self.jobs.complete(c, job.id)
        finally:
            metrics.JOB_DURATION.labels(job.type.value).observe(time.monotonic() - t0)
            request_id_var.reset(token)
        return True

    def run_until_idle(self, max_jobs: int = 1000) -> int:
        n = 0
        while n < max_jobs and self.run_once():
            n += 1
        return n

    def run_forever(self, on_tick: Callable[[], None] | None = None) -> None:
        while not self.stop.is_set():
            got = self.run_once()
            if on_tick:
                on_tick()
            if not got:
                self.stop.wait(self.poll_s)
