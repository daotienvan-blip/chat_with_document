"""Composition root: nơi duy nhất nối adapter vào lõi (S0-05)."""
from __future__ import annotations

from dataclasses import dataclass, field

from cwd_server.adapters.llm_local import ExtractiveLlm, FakeLlm
from cwd_server.adapters.pymupdf_extractor import PyMuPdfExtractor
from cwd_server.adapters.resilient_llm import ResilientLlm
from cwd_server.adapters.stores import InMemoryObjectStore, LocalFsObjectStore
from cwd_server.core.answer.service import AnswerService
from cwd_server.core.documents.service import DocumentService
from cwd_server.core.guard import LoadGuard, RateLimiter
from cwd_server.core.ingestion.chunker import Chunker
from cwd_server.core.ingestion.service import IngestionService
from cwd_server.core.retrieval.service import RetrievalService
from cwd_server.persistence.db import Database
from cwd_server.persistence.repositories import ChunkRepository, DocumentRepository, JobRepository
from cwd_server.platform import metrics
from cwd_server.platform.config import Settings


def build_llm(s: Settings):
    if s.llm_provider == "http":
        from cwd_server.adapters.llm_http import HttpLlm
        return HttpLlm(s.llm_base_url or "", s.llm_api_key, s.llm_embed_model or "", s.llm_chat_model or "",
                       s.embedding_dim, s.llm_temperature, s.llm_embed_timeout_s, s.llm_generate_timeout_s)
    if s.llm_provider == "fake":
        return FakeLlm(s.embedding_dim)
    return ExtractiveLlm(s.embedding_dim)


def build_store(s: Settings):
    if s.object_store == "memory":
        return InMemoryObjectStore()
    if s.object_store == "s3":
        from cwd_server.adapters.s3_store import S3ObjectStore
        return S3ObjectStore(s.s3_endpoint, s.s3_bucket, s.s3_access_key, s.s3_secret_key, s.s3_region)
    return LocalFsObjectStore(s.storage_dir)


@dataclass
class Container:
    settings: Settings
    db: Database
    store: object
    raw_llm: object
    llm: ResilientLlm
    docs: DocumentRepository = field(default_factory=DocumentRepository)
    chunks: ChunkRepository = field(default_factory=ChunkRepository)
    jobs: JobRepository = field(default_factory=JobRepository)
    extractor: object = None

    def __post_init__(self):
        s = self.settings
        self.extractor = self.extractor or PyMuPdfExtractor(s.pdf_timeout_s, s.pdf_memory_mb)
        self.documents = DocumentService(self.db, self.docs, self.jobs, self.store, s.purge_delay_s)
        self.ingestion = IngestionService(self.db, self.docs, self.chunks, self.store, self.extractor, self.llm,
                                          Chunker(s.rag_chunk_tokens, s.rag_chunk_overlap, s.rag_chunk_max_chars),
                                          s.embedding_dim, s.embed_batch_size)
        self.retrieval = RetrievalService(self.db, self.chunks, self.llm, s)
        self.answers = AnswerService(self.db, self.chunks, self.retrieval, self.llm, s.rag_min_relevance,
                                     on_status=lambda st: metrics.ANSWERS.labels(st.value).inc(),
                                     on_downgrade=metrics.GROUNDING_DOWNGRADES.inc)
        self.question_guard = LoadGuard(s.load_max_concurrent_questions, s.load_wait_s)
        self.upload_guard = LoadGuard(s.load_max_concurrent_uploads, s.load_wait_s)
        self.rate_limiter = RateLimiter({"questions": s.rate_questions_per_min, "uploads": s.rate_uploads_per_min,
                                         "other": s.rate_other_per_min})


def build_container(s: Settings, *, store=None, llm=None, extractor=None, sleep=None) -> Container:
    raw = llm or build_llm(s)
    kw = {"sleep": sleep} if sleep else {}
    return Container(settings=s, db=Database(s.database_url, s.db_pool_size), store=store or build_store(s),
                     raw_llm=raw, llm=ResilientLlm(raw, **kw), extractor=extractor)
