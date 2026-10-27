from __future__ import annotations

import io
import os

import pytest
from sqlalchemy import create_engine, text

from cwd_server.adapters.llm_local import FakeLlm
from cwd_server.adapters.stores import InMemoryObjectStore
from cwd_server.persistence.db import render_schema
from cwd_server.platform.config import Settings

TEST_DB = os.environ.get("TEST_DATABASE_URL", "postgresql+psycopg:///cwd_test")
DIM = 64


def test_settings(**over) -> Settings:
    base = dict(database_url=TEST_DB, object_store="memory", llm_provider="fake", embedding_dim=DIM,
                rate_limit_enabled=False, web_dist="/nonexistent", rag_chunk_tokens=80, rag_chunk_overlap=10,
                pdf_timeout_s=30)
    base.update(over)
    return Settings(_env_file=None, **base)


@pytest.fixture(scope="session")
def _schema():
    eng = create_engine(TEST_DB)
    s = test_settings()
    with eng.begin() as c:
        c.execute(text("DROP TABLE IF EXISTS jobs, chunks, documents, alembic_version CASCADE"))
        c.execute(text(render_schema(s.schema_sql, DIM)))
    eng.dispose()


@pytest.fixture
def clean_db(_schema):
    eng = create_engine(TEST_DB)
    with eng.begin() as c:
        c.execute(text("TRUNCATE jobs, chunks, documents"))
    eng.dispose()


@pytest.fixture
def fake_llm():
    return FakeLlm(DIM)


@pytest.fixture
def store():
    return InMemoryObjectStore()


@pytest.fixture
def container(clean_db, fake_llm, store):
    from cwd_server.container import build_container
    c = build_container(test_settings(), store=store, llm=fake_llm, sleep=lambda s: None)
    yield c
    c.db.engine.dispose()


@pytest.fixture
def client(container):
    from fastapi.testclient import TestClient

    from cwd_server.api.app import create_app
    with TestClient(create_app(container)) as tc:
        yield tc


@pytest.fixture
def runner(container):
    from cwd_server.worker.__main__ import build_runner
    r, _ = build_runner(container)
    return r


def upload(client, data: bytes, name: str = "tai-lieu.pdf"):
    return client.post("/api/v1/documents", files={"file": (name, io.BytesIO(data), "application/pdf")})
