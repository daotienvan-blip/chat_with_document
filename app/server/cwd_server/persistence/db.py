"""Engine và giao dịch (SQLAlchemy 2, đồng bộ)."""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Connection, Engine, create_engine, text


class Database:
    def __init__(self, url: str, pool_size: int = 10):
        self.engine: Engine = create_engine(url, pool_size=pool_size, max_overflow=5, pool_pre_ping=True)

    @contextmanager
    def tx(self) -> Iterator[Connection]:
        with self.engine.begin() as conn:
            yield conn

    @contextmanager
    def read(self) -> Iterator[Connection]:
        with self.engine.connect() as conn:
            yield conn

    def ping(self) -> None:
        with self.engine.connect() as c:
            c.execute(text("SELECT 1"))


def render_schema(schema_path: str, embedding_dim: int) -> str:
    """Đọc docs/04-design/schema.sql, thay số chiều vector theo cấu hình [TBD: OQ-S01]."""
    sql = Path(schema_path).read_text(encoding="utf-8")
    if "vector(1536)" not in sql:
        raise RuntimeError("schema.sql không còn 'vector(1536)'; cập nhật render_schema")
    return sql.replace("vector(1536)", f"vector({int(embedding_dim)})")


def to_vector_literal(vec: list[float]) -> str:
    return "[" + ",".join(f"{x:.6f}" for x in vec) + "]"
