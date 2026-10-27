"""Lược đồ ban đầu: thực thi docs/04-design/schema.sql (không chép tay).

Revision ID: 0001_init
"""
from alembic import op

from cwd_server.persistence.db import render_schema
from cwd_server.platform.config import get_settings

revision = "0001_init"
down_revision = None


def upgrade() -> None:
    s = get_settings()
    op.execute(render_schema(s.schema_sql, s.embedding_dim))


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS jobs, chunks, documents CASCADE")
