"""Cấu hình từ biến môi trường (S0-03). Giá trị chưa quyết định để None, không bịa số."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR = Path(__file__).resolve().parents[3]  # .../app
REPO_DIR = APP_DIR.parent  # .../chat_with_document


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(APP_DIR / ".env"), extra="ignore")

    database_url: str = "postgresql+psycopg:///cwd"
    db_pool_size: int = 10

    object_store: Literal["local", "memory", "s3"] = "local"
    storage_dir: str = str(APP_DIR / "var" / "storage")
    s3_endpoint: str | None = None
    s3_bucket: str = "cwd-documents"
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_region: str | None = None

    # "extractive" = AI giả trích xuất chạy cục bộ (demo); "fake" = kịch bản cho test; "http" = API tương thích OpenAI
    llm_provider: Literal["extractive", "fake", "http"] = "extractive"
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_embed_model: str | None = None
    llm_chat_model: str | None = None
    embedding_dim: int = 384  # [TBD: OQ-S01]
    llm_temperature: float = 0.0
    llm_embed_timeout_s: float = 10.0
    llm_generate_timeout_s: float = 30.0

    max_file_size_mb: int | None = None  # [TBD: OQ-009]
    hard_max_upload_mb: int = 200  # [Đề xuất] chặn tải không giới hạn khi giới hạn nghiệp vụ còn null
    max_question_length: int | None = None  # [TBD: OQ-P06]
    hard_max_question_chars: int = 4000  # [Đề xuất] chặn câu hỏi không giới hạn khi giới hạn nghiệp vụ còn null (F-03)
    language: str | None = None  # [TBD: OQ-011]
    poll_interval_ms: int = 2000

    rag_chunk_tokens: int = 600
    rag_chunk_overlap: int = 100
    rag_chunk_max_chars: int = 8000
    rag_top_k_vector: int = 20
    rag_top_k_fts: int = 20
    rag_rrf_k: int = 60
    rag_context_chunks: int = 8
    rag_max_chunks_per_doc: int = 4
    rag_min_relevance: float = 0.0  # [TBD: hiệu chỉnh bằng DEP-002/OQ-004]; 0 = chỉ chặn khi rỗng
    retrieval_mode: Literal["exact", "hnsw"] = "exact"  # theo spike S3-00
    hnsw_ef_search: int = 100
    embed_batch_size: int = 64

    pdf_timeout_s: float = 120.0
    pdf_memory_mb: int = 1024
    purge_delay_s: int = 3600
    worker_poll_s: float = 1.0
    sweep_interval_s: int = 300
    reconcile_interval_s: int = 3600
    orphan_age_s: int = 86400
    job_lock_minutes: int = 10

    load_max_concurrent_questions: int = 8
    load_max_concurrent_uploads: int = 4
    load_wait_s: float = 2.0
    rate_limit_enabled: bool = True
    rate_questions_per_min: int = 30
    rate_uploads_per_min: int = 10
    rate_other_per_min: int = 120
    trust_proxy: bool = False

    web_dist: str = str(APP_DIR / "web" / "dist")
    schema_sql: str = str(REPO_DIR / "docs" / "04-design" / "schema.sql")


@lru_cache
def get_settings() -> Settings:
    return Settings()
