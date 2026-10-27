"""LoadGuard và giới hạn tốc độ (S7-01)."""
from __future__ import annotations

import math
import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager

from cwd_server.core.errors import RateLimited, SystemBusy


class LoadGuard:
    def __init__(self, max_concurrent: int, wait_s: float, retry_after: int = 5):
        self._sem = threading.BoundedSemaphore(max_concurrent)
        self.wait_s, self.retry_after = wait_s, retry_after

    @contextmanager
    def slot(self) -> Iterator[None]:
        if not self._sem.acquire(timeout=self.wait_s):
            raise SystemBusy("Hệ thống đang bận. Tài liệu của bạn không bị mất. Vui lòng thử lại.",
                             retry_after=self.retry_after)
        try:
            yield
        finally:
            self._sem.release()


class RateLimiter:
    """Token bucket theo (khóa khách, nhóm)."""

    def __init__(self, limits_per_min: dict[str, int], clock: Callable[[], float] = time.monotonic):
        self.limits = limits_per_min
        self.clock = clock
        self._buckets: dict[tuple[str, str], tuple[float, float]] = {}
        self._lock = threading.Lock()

    def hit(self, client: str, group: str) -> None:
        cap = self.limits[group]
        rate = cap / 60.0
        now = self.clock()
        with self._lock:
            tokens, last = self._buckets.get((client, group), (float(cap), now))
            tokens = min(cap, tokens + (now - last) * rate)
            if tokens < 1.0:
                self._buckets[(client, group)] = (tokens, now)
                raise RateLimited("Bạn thao tác quá nhanh. Vui lòng thử lại sau ít giây.",
                                  retry_after=max(1, math.ceil((1.0 - tokens) / rate)))
            self._buckets[(client, group)] = (tokens - 1.0, now)
