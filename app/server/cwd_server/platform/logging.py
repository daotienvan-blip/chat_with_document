"""Log JSON có cấu trúc. Không bao giờ ghi nội dung câu hỏi, câu trả lời hay văn bản tài liệu (SAD §4.3)."""
from __future__ import annotations

import contextvars
import json
import logging
import sys
import time

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)

_ALLOWED = {"event", "durationMs", "errorCode", "documentId", "jobId", "status", "path", "method", "count", "pages"}


class JsonFormatter(logging.Formatter):
    def __init__(self, service: str):
        super().__init__()
        self.service = service

    def format(self, record: logging.LogRecord) -> str:
        out = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)) + "Z",
            "level": record.levelname.lower(),
            "service": self.service,
            "requestId": getattr(record, "requestId", None) or request_id_var.get(),
            "msg": record.getMessage(),
        }
        for k in _ALLOWED:
            if hasattr(record, k):
                out[k] = getattr(record, k)
        if record.exc_info:
            out["exc"] = record.exc_info[0].__name__ if record.exc_info[0] else None
        return json.dumps(out, ensure_ascii=False)


def setup_logging(service: str, level: int = logging.INFO) -> None:
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(JsonFormatter(service))
    root.addHandler(h)
    root.setLevel(level)
    for noisy in ("uvicorn.access",):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def log(logger: logging.Logger, msg: str, level: int = logging.INFO, **fields) -> None:
    unknown = set(fields) - _ALLOWED - {"requestId"}
    if unknown:
        raise ValueError(f"trường log không cho phép: {unknown}")
    logger.log(level, msg, extra=fields)
