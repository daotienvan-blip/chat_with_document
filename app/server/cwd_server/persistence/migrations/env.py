"""Alembic env: URL lấy từ Settings (hoặc -x url=...)."""
from alembic import context
from sqlalchemy import create_engine

from cwd_server.platform.config import get_settings

url = context.get_x_argument(as_dictionary=True).get("url") or get_settings().database_url
engine = create_engine(url)
with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=None)
    with context.begin_transaction():
        context.run_migrations()
