"""`python -m cwd_server.worker` — tiến trình xử lý nền (S2-05)."""
from __future__ import annotations

import logging
import signal
import threading
import time
from datetime import UTC, datetime

from cwd_server.container import Container, build_container
from cwd_server.core.types import JobType
from cwd_server.platform.config import get_settings
from cwd_server.platform.logging import setup_logging
from cwd_server.worker.maintenance import Maintenance
from cwd_server.worker.runner import Runner

log = logging.getLogger("cwd.worker")


def build_runner(c: Container) -> tuple[Runner, Maintenance]:
    m = Maintenance(c.db, c.docs, c.jobs, c.store, c.settings.orphan_age_s)

    def reopen_at():
        b = c.llm.breaker
        if b.opened_at is None:
            return None
        return datetime.fromtimestamp(time.time() + max(0.0, b.reopen_at() - b.clock()), UTC)

    handlers = {JobType.PROCESS_DOCUMENT: lambda job: c.ingestion.process(job.document_id),
                JobType.PURGE_DOCUMENT: m.purge}
    return Runner(c.db, c.jobs, c.docs, handlers, c.settings.job_lock_minutes, c.settings.worker_poll_s,
                  breaker_reopen_at=reopen_at), m


def main() -> None:
    setup_logging("worker")
    s = get_settings()
    runner, m = build_runner(build_container(s))
    last = {"sweep": 0.0, "reconcile": 0.0}

    def tick():
        now = time.monotonic()
        if now - last["sweep"] >= s.sweep_interval_s:
            last["sweep"] = now
            m.sweep()
        if now - last["reconcile"] >= s.reconcile_interval_s:
            last["reconcile"] = now
            log.info("đối soát", extra={"event": "reconcile", "count": sum(m.reconcile().values())})

    def stop(signum, _frame):
        log.info("dừng êm", extra={"event": "shutdown"})
        runner.stop.set()  # hoàn tất việc hiện tại rồi thoát

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    log.info("worker khởi động", extra={"event": "start"})
    t = threading.Thread(target=runner.run_forever, kwargs={"on_tick": tick}, daemon=False)
    t.start()
    while t.is_alive():
        t.join(0.5)


if __name__ == "__main__":
    main()
