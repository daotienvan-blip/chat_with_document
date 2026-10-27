#!/usr/bin/env bash
# Khôi phục CSDL từ bản dump rồi đối soát kho ↔ CSDL (S8-07, S7-04).
# Dùng: deploy/restore.sh TỆP_DUMP [DB_ĐÍCH]   — DB_ĐÍCH bị tạo lại (XÓA dữ liệu hiện có).
set -euo pipefail
PG=${PG_BIN:-/opt/homebrew/opt/postgresql@17/bin}
DUMP=$1
DB=${2:-cwd}
"$PG/dropdb" --if-exists "$DB"
"$PG/createdb" "$DB"
"$PG/pg_restore" -d "$DB" --no-owner "$DUMP"
APP="$(cd "$(dirname "$0")/.." && pwd)"
cd "$APP/server" && DATABASE_URL="postgresql+psycopg:///$DB" .venv/bin/python -c "
from cwd_server.container import build_container
from cwd_server.platform.config import get_settings
from cwd_server.worker.maintenance import Maintenance
c = build_container(get_settings())
print('đối soát:', Maintenance(c.db, c.docs, c.jobs, c.store, c.settings.orphan_age_s).reconcile())"
