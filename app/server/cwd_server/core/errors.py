"""Lỗi miền. `code` khớp ProblemCode trong openapi.yaml; tầng API ánh xạ sang HTTP."""
from __future__ import annotations


class DomainError(Exception):
    code = "INTERNAL_ERROR"

    def __init__(self, detail: str | None = None, *, limit: int | None = None, retry_after: int | None = None):
        super().__init__(detail or self.code)
        self.detail = detail
        self.limit = limit
        self.retry_after = retry_after


class InvalidRequest(DomainError):
    code = "INVALID_REQUEST"


class UnsupportedType(DomainError):
    code = "UNSUPPORTED_TYPE"


class FileTooLarge(DomainError):
    code = "FILE_TOO_LARGE"


class EmptyQuestion(DomainError):
    code = "EMPTY_QUESTION"


class QuestionTooLong(DomainError):
    code = "QUESTION_TOO_LONG"


class NotFound(DomainError):
    code = "NOT_FOUND"


class RateLimited(DomainError):
    code = "RATE_LIMITED"


class SystemBusy(DomainError):
    code = "SYSTEM_BUSY"


class StorageUnavailable(DomainError):
    code = "STORAGE_UNAVAILABLE"


class AiUnavailable(DomainError):
    code = "AI_UNAVAILABLE"

    def __init__(self, detail: str | None = None, *, breaker_open: bool = False, **kw):
        super().__init__(detail, **kw)
        self.breaker_open = breaker_open


class AiTimeout(DomainError):
    code = "AI_TIMEOUT"


# --- lỗi nội bộ (không trả trực tiếp cho người dùng) ---
class AiBadOutput(Exception):
    """Đầu ra LLM không đúng schema."""


class PdfCorrupt(Exception):
    pass


class PdfEncrypted(Exception):
    pass


class PdfTimeout(Exception):
    """Trích văn bản vượt thời gian — lỗi tạm thời, thử lại được."""


class RetryableError(Exception):
    """Việc nền gặp lỗi tạm thời; Runner sẽ xếp lại theo lịch lùi."""

    def __init__(self, message: str, *, count_attempt: bool = True):
        super().__init__(message)
        self.count_attempt = count_attempt


class ConfigurationError(Exception):
    pass
