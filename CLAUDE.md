# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

"Chat với tài liệu" MVP: upload PDFs, ask questions, get answers citing (document, page) or "not found". Code lives in `app/`; SDLC docs (requirements → design → verification → release/ops) live in `docs/`. Docs, comments, commit messages and user-facing strings are in Vietnamese — keep it that way.

## Commands

All `make` targets run from `app/` (macOS + Homebrew paths are hard-coded in the Makefile).

```bash
make setup        # server/.venv (Python 3.12, pip -e '.[dev]') + web npm install
make check        # ruff + import-linter + unit tests + web tsc/vitest (fast loop; no mypy, no integration tests)
make ci           # full L0 gate, mirrors .github/workflows/ci.yml (adds mypy, integration, coverage, gitleaks, docker build); logs in var/ci/
make test-int     # integration tests on real PostgreSQL (DB cwd_test, Homebrew pg17 via db-up)
make demo         # build web, generate sample PDFs, run api+worker on :8000, smoke test; `make stop` to stop
make up / down    # Docker (Colima) dev stack: pg17+pgvector on :5433, SeaweedFS S3 on :9000
make prod-up      # prod-like compose (api×2, worker, nginx TLS) at https://localhost:8443; `make proxy-test`, `make prod-down`
make eval         # answer-quality eval (eval_cwd) · make trace  # list USER_STORIES ACs with no test
```

Single test (from `app/server`):
```bash
.venv/bin/pytest tests/unit/test_adapters.py::test_name
.venv/bin/pytest -m integration tests/integration/test_flows.py::test_name   # needs a DB
```
- `pyproject.toml` sets `addopts = "-q -m 'not integration'"`: plain `pytest` skips integration tests; CI uses `-m "integration or not integration"`.
- Integration tests use `TEST_DATABASE_URL` (default `postgresql+psycopg:///cwd_test`; for the Docker stack use `...cwd:cwd@localhost:5433/cwd_test`). They **drop and recreate** `jobs`, `chunks` and `documents` in that database, so never point it at a database holding real data.
- `tests/integration/test_privileges.py` connects with `host="localhost"`, so inside a container it needs the DB reachable on localhost (e.g. `--network host`).
- PDF fixtures (`tests/fixtures/pdfs.py`) need a Vietnamese-capable font (DejaVu); without it they raise instead of silently producing `?`.
- Local macOS arm64 can pass while the x86_64 Linux runner fails (the PyMuPDF 2.0 failure did). To reproduce a CI-only failure, run the tests in `ubuntu:24.04` with `--platform linux/amd64` as a non-root user.
- Coverage gate is 70% (unit + integration combined). Web: `npx tsc -b --noEmit`, `npx vitest run`, single test `npx vitest run <file>`.

## Architecture (server: `app/server/cwd_server`)

Hexagonal layout, enforced by import-linter contracts in `pyproject.toml` (`lint-imports` fails CI):
- `core/` (domain services: documents, ingestion, retrieval, answer, guard) and `ports/` (Protocols: `LlmPort`, `ObjectStorePort`, `PdfExtractorPort`) must not import `adapters`, `persistence`, `api`, `worker`.
- Only `adapters/` may import external SDKs (`fitz`/PyMuPDF, `boto3`, `httpx`).
- `container.py` is the single composition root: picks adapters from `Settings` (`platform/config.py`, env-driven) — `LLM_PROVIDER` = `extractive` (default, local fake that only quotes sentences from the docs) | `fake` | `http` (real AI; only allowed once data policy OQ-005 permits); `OBJECT_STORE` = `local` | `memory` | `s3`. Tests build containers via `build_container(..., llm=, store=, extractor=)`.

Flow:
- **Upload** (`api/app.py` → `DocumentService`) stores the file and enqueues a job in PostgreSQL. **Worker** (`worker/runner.py`, `python -m cwd_server.worker`) claims jobs with `FOR UPDATE SKIP LOCKED`, with retry/backoff, then runs `IngestionService`: extract → chunk → embed → pgvector. The worker also runs `worker/maintenance.py` (purge, orphan sweep, reconcile against the object store). All HTTP routes are in `api/app.py`; `api/routers/` is empty.
- PDF extraction runs in a **subprocess with `RLIMIT_AS`** (`adapters/pymupdf_extractor.py`, `pdf_memory_mb`). Exit codes map to domain errors (`PdfCorrupt`, `PdfEncrypted`); abnormal death → `PdfExtractorCrashed` → `PROCESSING_ERROR`, never `FILE_CORRUPT`. PyMuPDF is pinned `<2` because 2.0 imports numpy/onnxruntime and blows the memory limit on x86_64.
- **Ask** → `RetrievalService` → `AnswerService` with grounding gates: G-L1 (no relevant chunks ⇒ not_found without calling the LLM), G-L2 (drop citations not in the sent set; none left ⇒ not_found), G-L3 (source names/pages come from DB metadata, never from LLM text). `adapters/resilient_llm.py` wraps the LLM with retry (backoff + jitter) and a circuit breaker; timeouts are set in `adapters/llm_http.py`.
- API errors are RFC 7807 problem+json (`api/problems.py`); responses in integration tests are validated against `docs/04-design/openapi.yaml` (`tests/support/openapi_assert.py`). The web client types are generated from the same file (`npm run gen:api`).
- `docs/04-design/schema.sql` is executed at runtime, not just documentation: migration `0001_init` and the test fixture (`tests/conftest.py`) both render it, and the test fixture does not run Alembic. A later migration alone would not reach the test schema, and editing `schema.sql` does not change databases already migrated.
- Prometheus metrics in `platform/metrics.py`; logs are structured with an `event` field and must never contain document content or question text.

Web (`app/web`): React 18 + Vite + TanStack Query; `features/{documents,chat,sources}`. In demo mode the built `dist/` is served by the api on :8000.

Deploy (`app/deploy`): Dockerfiles, `compose.{dev,prod}.yaml`, nginx proxy config + `proxy/proxy-test.sh` (request-size and rate limits live in `proxy/nginx.conf` too), backup/restore scripts. Operational procedures: `docs/05-implement/runbook.md`, `docs/10-operations/runbook.md`.

## Process rules

- Tests carry requirement IDs: `@pytest.mark.req("US-010-AC1")` (web: `[US-xxx-ACn]` in test names); `make trace` checks coverage against `docs/03-analysis/USER_STORIES.md`.
- `docs/diagrams/use-case-diagram.drawio` is the source of truth for MVP scope; values not yet decided are marked `[TBD: OQ-…]`/`[Đề xuất]` in config and docs, and are not invented.
- PRs ≤ 400 lines, CI green, approved by someone other than the author. The agent may branch, commit and open PRs when asked, but must not approve, merge, deploy, or change production. Bugs found go in `docs/07-verification/review-record.md` / `docs/05-implement/release-gates.md`; incidents in `docs/10-operations/incidents/`.
- When fixing a defect, update the matching gate/record doc in the same PR.
