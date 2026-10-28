#!/usr/bin/env bash
# L0 cục bộ: cùng các bước với .github/workflows/ci.yml. Chạy từ app/ qua `make ci`.
set -uo pipefail
export PATH=/opt/homebrew/bin:$PATH
OUT=var/ci
T0=$(date +%s)
FAIL=0
step() {
  local name=$1; shift
  local s=$(date +%s)
  echo "::: $name"
  if "$@"; then echo "::: PASS $name ($(( $(date +%s) - s ))s)"; else echo "::: FAIL $name"; FAIL=1; fi
}
echo "::: commit $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- . || echo ' +thay đổi chưa commit') · $(date '+%F %T')"

cd server
step "ruff" .venv/bin/ruff check cwd_server tests scripts
step "mypy" .venv/bin/mypy cwd_server
step "import-linter" .venv/bin/lint-imports
step "pytest unit+tích hợp, coverage ≥ 70%" .venv/bin/pytest -p no:warnings -m "integration or not integration" \
  --cov --cov-report=term --cov-report=xml:../$OUT/server-coverage.xml --cov-report=html:../$OUT/server-htmlcov \
  --junitxml=../$OUT/server-junit.xml
cd ../web
step "tsc" npx tsc -b --noEmit
step "vitest + coverage ≥ 70%" npx vitest run --coverage
step "vite build" npx vite build --logLevel warn
cd ..
step "gitleaks (lịch sử git)" gitleaks git .. --redact --no-banner
if docker info >/dev/null 2>&1; then
  step "docker build server" docker build -q -f deploy/Dockerfile.server -t cwd-server:ci ..
  step "docker build web" docker build -q -f deploy/Dockerfile.web -t cwd-web:ci ..
else
  echo "::: SKIP docker build (Docker/Colima chưa chạy)"
fi
DUR=$(( $(date +%s) - T0 ))
echo "::: tổng thời gian ${DUR}s (giới hạn 600s)"
[ "$DUR" -le 600 ] || { echo "::: FAIL quá 10 phút"; FAIL=1; }
[ $FAIL -eq 0 ] && echo "::: L0 XANH" || echo "::: L0 ĐỎ"
exit $FAIL
