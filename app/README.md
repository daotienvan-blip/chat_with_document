# Chat với tài liệu — mã nguồn (MVP demo)

Tải PDF lên, đặt câu hỏi, nhận câu trả lời kèm nguồn (tài liệu, trang) hoặc “không tìm thấy”. Thiết kế: `../docs/04-design/`; kế hoạch: `../docs/05-implement/PLAN.md`; trạng thái: `../docs/05-implement/IMPLEMENTATION_STATUS.md`.

## Chạy demo (macOS, Homebrew)

```bash
brew install python@3.12 node postgresql@17 pgvector   # một lần
make setup        # venv + npm
make demo         # bật PostgreSQL, migrate, build web, sinh PDF minh họa, chạy api+worker, kiểm tra khói
# mở http://localhost:8000  — tải các tệp trong app/samples/ để thử
make stop
```

Bản demo dùng **AI giả trích xuất** chạy cục bộ: nó chọn câu trong tài liệu khớp từ khóa câu hỏi và trích nguồn, **không sinh nội dung mới** và không gửi dữ liệu ra ngoài. Bật AI thật (chỉ khi chính sách dữ liệu OQ-005 cho phép): đặt `LLM_PROVIDER=http` và `LLM_*` trong `app/.env`.

## Môi trường Docker (tùy chọn, S0-02)

```bash
brew install colima docker docker-compose   # một lần
make up      # Colima + PostgreSQL 17/pgvector (cổng 5433) + S3 SeaweedFS 4.50 (cổng 9000, bucket cwd-documents)
make down
```

Dùng stack này: bỏ chú thích khối “stack Docker” trong `.env.example` và chép vào `.env`. Chạy test tích hợp trên đó: `TEST_DATABASE_URL=postgresql+psycopg://cwd:cwd@localhost:5433/cwd_test make test-int`. Adapter S3 cần `pip install -e 'server[s3]'`.

Stack kiểu sản xuất (api×2, worker, nginx TLS): `make prod-up` → https://localhost:8443, `make proxy-test`, `make prod-down` — xem `docs/05-implement/runbook.md`.

## Cấu trúc

```text
app/
├── server/cwd_server/   api/ core/ ports/ adapters/ persistence/ worker/ platform/ container.py
├── server/tests/        unit/ integration/ support/ fixtures/
├── server/eval_cwd/     bộ đánh giá chất lượng (make eval)
├── server/scripts/      spike_hnsw.py, smoke.py, make_samples.py, trace_check.py
├── web/src/             app/ features/{documents,chat,sources} api-client/ components/ state/
└── deploy/              backup.sh, restore.sh, compose.*.yaml, Dockerfile.*, proxy/, prod-local/ (đã chạy thử trên Colima: `make prod-up`), DATA_LOCATION.md
```

## Lệnh

`make ci` (L0 = `.github/workflows/ci.yml`) · `make check` · `make test-int` · `make smoke` · `make eval` · `make trace` · `make spike` · `make logs` · `make db-up` / `make db-down`
