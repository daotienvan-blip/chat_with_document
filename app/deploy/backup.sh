#!/usr/bin/env bash
# Sao lưu CSDL (S8-07, Database_Design §5.2): pg_dump dạng custom, giữ 7 bản gần nhất.
# Dùng: deploy/backup.sh [DB] [THƯ_MỤC]   — mặc định DB=cwd, THƯ_MỤC=app/var/backups
# Tệp PDF gốc: bật versioning trên bucket (S3) hoặc sao lưu thư mục var/storage (bản demo cục bộ).
set -euo pipefail
PG=${PG_BIN:-/opt/homebrew/opt/postgresql@17/bin}
DB=${1:-cwd}
DIR=${2:-"$(cd "$(dirname "$0")/.." && pwd)/var/backups"}
mkdir -p "$DIR"
OUT="$DIR/$DB-$(date +%Y%m%d-%H%M%S).dump"
"$PG/pg_dump" -Fc -d "$DB" -f "$OUT"
ls -1t "$DIR"/"$DB"-*.dump | tail -n +8 | xargs -r rm -f
echo "$OUT"
