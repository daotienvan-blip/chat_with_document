"""Kiểu miền (Blueprint §3.2.1). Tên enum khớp openapi.yaml."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class DocumentStatus(StrEnum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class FailureReason(StrEnum):
    FILE_CORRUPT = "FILE_CORRUPT"
    FILE_ENCRYPTED = "FILE_ENCRYPTED"
    NO_EXTRACTABLE_TEXT = "NO_EXTRACTABLE_TEXT"
    PROCESSING_ERROR = "PROCESSING_ERROR"


class AnswerStatus(StrEnum):
    ANSWERED = "answered"
    PARTIAL = "partial"
    NOT_FOUND = "not_found"


class JobType(StrEnum):
    PROCESS_DOCUMENT = "process_document"
    PURGE_DOCUMENT = "purge_document"


@dataclass(frozen=True)
class Document:
    id: uuid.UUID
    name: str
    size_bytes: int
    page_count: int | None
    storage_key: str
    content_sha256: str
    status: DocumentStatus
    failure_reason: FailureReason | None
    created_at: datetime
    deleted_at: datetime | None = None


@dataclass(frozen=True)
class Page:
    number: int  # bắt đầu từ 1
    text: str


@dataclass(frozen=True)
class ChunkDraft:
    chunk_index: int
    page_start: int
    page_end: int
    text: str


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_name: str
    page_start: int
    page_end: int
    text: str
    score: float  # điểm RRF
    vector_score: float | None = None  # 1 - khoảng cách cosin, nếu có


@dataclass(frozen=True)
class SourceRef:
    document_id: uuid.UUID
    document_name: str
    pages: list[int]


@dataclass(frozen=True)
class AnswerResult:
    status: AnswerStatus
    answer: str
    sources: list[SourceRef] = field(default_factory=list)


@dataclass(frozen=True)
class Job:
    id: uuid.UUID
    type: JobType
    document_id: uuid.UUID
    attempts: int
    request_id: str | None
