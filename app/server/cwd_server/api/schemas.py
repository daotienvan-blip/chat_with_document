"""Schema phản hồi — đúng tên trường trong openapi.yaml, không thêm trường."""
from __future__ import annotations

from datetime import UTC
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from cwd_server.core.types import AnswerResult, Document


class ConfigOut(BaseModel):
    maxFileSizeMb: int | None
    maxQuestionLength: int | None
    language: str | None
    pollIntervalMs: int


class DocumentOut(BaseModel):
    id: UUID
    name: str
    sizeBytes: int
    pageCount: int | None
    status: Literal["processing", "ready", "failed"]
    failureReason: Literal["FILE_CORRUPT", "FILE_ENCRYPTED", "NO_EXTRACTABLE_TEXT", "PROCESSING_ERROR"] | None
    createdAt: str

    @classmethod
    def of(cls, d: Document) -> DocumentOut:
        ts = d.created_at.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        return cls(id=d.id, name=d.name, sizeBytes=d.size_bytes, pageCount=d.page_count, status=d.status.value,
                   failureReason=d.failure_reason.value if d.failure_reason else None, createdAt=ts)


class DocumentListOut(BaseModel):
    items: list[DocumentOut]
    total: int


class QuestionIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str


class SourceOut(BaseModel):
    documentId: UUID
    documentName: str
    pages: list[int]


class AnswerOut(BaseModel):
    status: Literal["answered", "partial", "not_found"]
    answer: str
    sources: list[SourceOut]

    @classmethod
    def of(cls, r: AnswerResult) -> AnswerOut:
        return cls(status=r.status.value, answer=r.answer,
                   sources=[SourceOut(documentId=s.document_id, documentName=s.document_name, pages=s.pages)
                            for s in r.sources])
