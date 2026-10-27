# "Chat với tài liệu" (MVP) — lệnh phát triển và demo. Chạy từ thư mục app/.
SHELL := /bin/bash
export PATH := /opt/homebrew/bin:$(PATH)
PY      := server/.venv/bin/python
PG      := /opt/homebrew/opt/postgresql@17/bin
PGDATA  := /opt/homebrew/var/postgresql@17
VAR     := var
PORT    ?= 8000

.PHONY: up down prod-env prod-up prod-down prod-ps proxy-test setup check test-int contract trace db-up db-down migrate build-web samples run stop demo smoke spike eval e2e proxy-test llm-smoke logs

setup:                      ## cài phụ thuộc server + web
	cd server && /opt/homebrew/bin/python3.12 -m venv .venv && .venv/bin/pip install -q -e '.[dev]'
	cd web && npm install --no-audit --no-fund

check:                      ## lint + hợp đồng phụ thuộc + unit test server + typecheck/test web
	cd server && .venv/bin/ruff check cwd_server tests scripts && .venv/bin/lint-imports && .venv/bin/pytest -p no:warnings
	cd web && npx tsc -b --noEmit && npx vitest run

test-int: db-up             ## kiểm thử tích hợp trên PostgreSQL thật (CSDL cwd_test)
	cd server && .venv/bin/pytest -p no:warnings -m integration

contract: test-int          ## mọi phản hồi trong test tích hợp đã kiểm theo docs/04-design/openapi.yaml

trace:                      ## liệt kê AC của USER_STORIES chưa có test (S8-10)
	$(PY) server/scripts/trace_check.py

COMPOSE := docker-compose -f deploy/compose.dev.yaml

up:                         ## S0-02: PostgreSQL+pgvector (cổng 5433) + S3 SeaweedFS (9000) bằng Docker/Colima
	@colima status >/dev/null 2>&1 || colima start --cpu 2 --memory 3 --disk 20
	$(COMPOSE) up -d --wait postgres s3
	$(COMPOSE) run --rm s3-init

down:
	$(COMPOSE) down

db-up:
	@$(PG)/pg_ctl -D $(PGDATA) status >/dev/null 2>&1 || LC_ALL=en_US.UTF-8 $(PG)/pg_ctl -D $(PGDATA) -l /opt/homebrew/var/log/postgresql@17.log -w start
	@for db in cwd cwd_test; do $(PG)/psql -d postgres -Atc "select 1 from pg_database where datname='$$db'" | grep -q 1 || $(PG)/createdb $$db; done

db-down:
	$(PG)/pg_ctl -D $(PGDATA) stop

migrate: db-up
	cd server && .venv/bin/alembic upgrade head

build-web:
	cd web && npm run build

samples:                    ## sinh PDF minh họa vào app/samples
	cd server && .venv/bin/python scripts/make_samples.py ../samples

run: migrate               ## chạy api (cổng $(PORT), phục vụ luôn web đã build) + worker ở nền
	@mkdir -p $(VAR)/log $(VAR)/run
	@$(MAKE) --no-print-directory stop >/dev/null
	@cd server && { nohup .venv/bin/uvicorn cwd_server.api.main:app --host 127.0.0.1 --port $(PORT) \
		--timeout-graceful-shutdown 45 < /dev/null > ../$(VAR)/log/api.log 2>&1 & echo $$! > ../$(VAR)/run/api.pid; disown; }
	@cd server && { nohup .venv/bin/python -m cwd_server.worker < /dev/null > ../$(VAR)/log/worker.log 2>&1 & \
		echo $$! > ../$(VAR)/run/worker.pid; disown; }
	@for i in $$(seq 1 40); do curl -sf localhost:$(PORT)/readyz >/dev/null && break; sleep 0.25; done
	@curl -sf localhost:$(PORT)/readyz >/dev/null && echo "Đang chạy: http://localhost:$(PORT)" || (echo "API chưa sẵn sàng, xem $(VAR)/log/api.log"; exit 1)

stop:                       ## dừng api + worker (tắt êm)
	@for p in api worker; do [ -f $(VAR)/run/$$p.pid ] && kill $$(cat $(VAR)/run/$$p.pid) 2>/dev/null; rm -f $(VAR)/run/$$p.pid; done; echo "đã dừng"

demo: build-web samples run smoke   ## build + chạy + kiểm tra khói

smoke:                      ## kiểm tra khói đầu-cuối trên hệ thống đang chạy
	$(PY) server/scripts/smoke.py http://localhost:$(PORT) samples

spike:                      ## S3-00: HNSW vs quét chính xác (XÓA dữ liệu cwd_test)
	cd server && .venv/bin/python scripts/spike_hnsw.py

eval: db-up                 ## S8-04: bộ đánh giá chất lượng (AI giả, bộ câu hỏi tổng hợp)
	cd server && .venv/bin/python -m eval_cwd.run

logs:
	tail -n 30 $(VAR)/log/api.log $(VAR)/log/worker.log

# ---- S8-05/S8-06: thử compose.prod.yaml cục bộ (Colima). Bí mật sinh ngẫu nhiên vào var/prod-local/ (không commit).
PL    := $(VAR)/prod-local
PROD  := docker-compose -p cwd-prod --project-directory .. --env-file $(PL)/compose.env \
         -f deploy/compose.prod.yaml -f deploy/compose.prod.local.yaml
PROXY_URL := https://localhost:8443

prod-env:
	@mkdir -p $(PL)/certs
	@[ -f $(PL)/compose.env ] || { r() { openssl rand -hex 16; }; A=$$(r); O=$$(r); W=$$(r); K=$$(r); \
	  printf '%s\n' "CWD_ENV_FILE=app/$(PL)/app.env" "TLS_DIR=./app/$(PL)/certs" "PROXY_PORT=8443" \
	    "POSTGRES_ADMIN_PASSWORD=$$K" "CWD_OWNER_PASSWORD=$$O" "CWD_API_PASSWORD=$$A" "CWD_WORKER_PASSWORD=$$W" \
	    "DATABASE_URL_MIGRATE=postgresql+psycopg://cwd_owner:$$O@db/cwd" \
	    "DATABASE_URL_API=postgresql+psycopg://cwd_api_login:$$A@db/cwd" \
	    "DATABASE_URL_WORKER=postgresql+psycopg://cwd_worker_login:$$W@db/cwd" > $(PL)/compose.env; }
	@printf '%s\n' OBJECT_STORE=s3 S3_ENDPOINT=http://s3:8333 S3_BUCKET=cwd-documents S3_ACCESS_KEY=cwd \
	  S3_SECRET_KEY=cwd-dev-secret S3_REGION=us-east-1 LLM_PROVIDER=extractive EMBEDDING_DIM=384 > $(PL)/app.env
	@[ -f $(PL)/certs/tls.crt ] || openssl req -x509 -newkey rsa:2048 -nodes -days 30 -subj /CN=localhost \
	  -addext subjectAltName=DNS:localhost -keyout $(PL)/certs/tls.key -out $(PL)/certs/tls.crt 2>/dev/null
	@chmod 644 $(PL)/certs/tls.key

prod-up: prod-env           ## build ảnh + chạy compose.prod (proxy https://localhost:8443)
	@colima status >/dev/null 2>&1 || colima start --cpu 2 --memory 3 --disk 20
	$(PROD) up -d --build --wait
	@curl -skf $(PROXY_URL)/readyz && echo " — $(PROXY_URL)"

prod-down:
	$(PROD) down -v

prod-ps:
	$(PROD) ps

proxy-test:                 ## S8-06: kiểm proxy trên stack prod-up
	deploy/proxy/proxy-test.sh $(PROXY_URL)

e2e llm-smoke:
	@echo "$@: chưa triển khai trên máy này (cần Docker/Playwright/khóa AI) — xem docs/05-implement/IMPLEMENTATION_STATUS.md"
