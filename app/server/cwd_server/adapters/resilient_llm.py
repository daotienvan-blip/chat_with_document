"""Bọc LlmPort: thử lại có lùi + nhiễu và circuit breaker (S7-02, SAD §4.2, Blueprint §3.7.5)."""
from __future__ import annotations

import random
import threading
import time
from collections.abc import Callable

from cwd_server.core.errors import AiBadOutput, AiTimeout, AiUnavailable
from cwd_server.platform import metrics


class CircuitBreaker:
    def __init__(self, threshold: int = 5, open_seconds: float = 30.0, clock: Callable[[], float] = time.monotonic):
        self.threshold, self.open_seconds, self.clock = threshold, open_seconds, clock
        self.failures = 0
        self.opened_at: float | None = None
        self.trial_in_flight = False
        self._lock = threading.Lock()

    @property
    def state(self) -> str:
        if self.opened_at is None:
            return "closed"
        return "half_open" if self.clock() - self.opened_at >= self.open_seconds else "open"

    def reopen_at(self) -> float:
        return (self.opened_at or self.clock()) + self.open_seconds

    def before(self) -> None:
        with self._lock:
            st = self.state
            if st == "open" or (st == "half_open" and self.trial_in_flight):
                raise AiUnavailable("breaker mở", breaker_open=True)
            if st == "half_open":
                self.trial_in_flight = True

    def success(self) -> None:
        with self._lock:
            self.failures, self.opened_at, self.trial_in_flight = 0, None, False
            metrics.BREAKER_OPEN.set(0)

    def failure(self) -> None:
        with self._lock:
            self.trial_in_flight = False
            if self.opened_at is not None:  # thử nửa mở thất bại ⇒ mở lại
                self.opened_at = self.clock()
                return
            self.failures += 1
            if self.failures >= self.threshold:
                self.opened_at = self.clock()
                metrics.BREAKER_OPEN.set(1)


class ResilientLlm:
    def __init__(self, inner, breaker: CircuitBreaker | None = None, embed_retries: int = 2,
                 generate_retries: int = 1, base_delay: float = 1.0, sleep: Callable[[float], None] = time.sleep):
        self.inner = inner
        self.breaker = breaker or CircuitBreaker()
        self.embed_retries, self.generate_retries = embed_retries, generate_retries
        self.base_delay, self.sleep = base_delay, sleep

    def _call(self, op: str, retries: int, fn):
        attempt = 0
        while True:
            self.breaker.before()
            t0 = time.monotonic()
            try:
                out = fn()
            except (AiUnavailable, AiTimeout) as e:
                self.breaker.failure()
                metrics.LLM_CALLS.labels(op, type(e).__name__).inc()
                if attempt >= retries or self.breaker.state != "closed":
                    raise
                delay = self.base_delay * (2 ** attempt) * random.uniform(0.7, 1.3)
                attempt += 1
                self.sleep(delay)
                continue
            except AiBadOutput:
                self.breaker.success()
                metrics.LLM_CALLS.labels(op, "bad_output").inc()
                raise
            self.breaker.success()
            metrics.LLM_CALLS.labels(op, "ok").inc()
            metrics.LLM_LATENCY.labels(op).observe(time.monotonic() - t0)
            return out

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self._call("embed", self.embed_retries, lambda: self.inner.embed(texts))

    def generate(self, system: str, user: str, schema: dict) -> dict:
        return self._call("generate", self.generate_retries, lambda: self.inner.generate(system, user, schema))
