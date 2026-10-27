#!/bin/sh
# Thử cục bộ compose.prod: CSDL cwd do cwd_owner sở hữu (chạy migrate), vai trò đăng nhập api/worker thuộc nhóm
# quyền tối thiểu của schema.sql (Database_Design §4.1). Mật khẩu đến từ tệp env sinh ngẫu nhiên (make prod-env).
set -eu
psql -v ON_ERROR_STOP=1 -U postgres <<SQL
CREATE ROLE cwd_owner LOGIN PASSWORD '${CWD_OWNER_PASSWORD}';
CREATE DATABASE cwd OWNER cwd_owner;
CREATE ROLE cwd_api NOLOGIN;
CREATE ROLE cwd_worker NOLOGIN;
CREATE ROLE cwd_api_login LOGIN PASSWORD '${CWD_API_PASSWORD}' IN ROLE cwd_api;
CREATE ROLE cwd_worker_login LOGIN PASSWORD '${CWD_WORKER_PASSWORD}' IN ROLE cwd_worker;
ALTER ROLE cwd_api_login SET statement_timeout = '30s';
SQL
psql -v ON_ERROR_STOP=1 -U postgres -d cwd -c "CREATE EXTENSION IF NOT EXISTS vector"
