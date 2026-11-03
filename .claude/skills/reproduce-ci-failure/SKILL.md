---
name: reproduce-ci-failure
description: Tái hiện lỗi chỉ xảy ra trên CI (Linux x86_64) của "Chat với tài liệu" khi máy cục bộ (macOS arm64) vẫn xanh. Dùng khi GitHub Actions đỏ mà `make check`/`make ci` cục bộ xanh.
---

# Tái hiện lỗi chỉ có trên CI

Máy cục bộ macOS arm64 có thể xanh trong khi runner Linux x86_64 đỏ. Ví dụ đã gặp: PyMuPDF 2.0 kéo numpy/onnxruntime và vượt giới hạn bộ nhớ `RLIMIT_AS` của tiến trình trích xuất PDF trên x86_64 (vì vậy PyMuPDF được ghim `<2`).

## Bước 1 — đọc log CI trước

Xác định job nào đỏ (`server`, `web`, `secrets`, `images` trong `.github/workflows/ci.yml`) và bước nào. Chỉ tái hiện khi log chưa đủ giải thích. Không đoán nguyên nhân từ tên bước.

## Bước 2 — chạy lại trong môi trường giống CI

Job `server` chạy trên `ubuntu-24.04`, Python 3.12, PostgreSQL `pgvector/pgvector:pg17`, font `fonts-dejavu-core`. Dùng Docker với:

- ảnh `ubuntu:24.04` và cờ `--platform linux/amd64` (Colima/Apple Silicon sẽ giả lập x86_64),
- **người dùng không phải root** (`-u`), vì một số hành vi quyền/giới hạn chỉ lộ ra khi không phải root,
- DB đạt được qua `localhost` (ví dụ `--network host`), vì `tests/integration/test_privileges.py` kết nối `host="localhost"`,
- `TEST_DATABASE_URL=postgresql+psycopg://cwd:cwd@localhost:5432/cwd_test` như trong workflow.

Trong container, lặp lại đúng các bước của job: `pip install -e '.[dev]'`, cài `fonts-dejavu-core`, rồi `ruff check`, `mypy cwd_server`, `lint-imports`, `pytest -p no:warnings -m "integration or not integration" --cov`.

Mẹo: chạy riêng test đỏ trước (`pytest <tệp>::<tên>`) để vòng lặp ngắn, sau đó mới chạy cả bộ.

## Bước 3 — sửa và ghi nhận

1. Sửa nguyên nhân gốc, không nới giới hạn (bộ nhớ, ngưỡng coverage, timeout) để cho qua.
2. Thêm ca hồi quy có mã AC nếu liên quan (xem skill `write-test-with-req-id`).
3. Ghi lỗi vào `docs/07-verification/review-record.md` / `docs/05-implement/release-gates.md` trong cùng PR; sự cố thật ghi ở `docs/10-operations/incidents/`.
