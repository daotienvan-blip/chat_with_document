# S0-01 — Khởi tạo repo, công cụ và quy ước kiểm thử

| | |
|---|---|
| **Lát cắt** | S0 — Khung chạy được (walking skeleton) (mốc M0) |
| **Cỡ** | S (1–3 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | Không |
| **Truy vết** | — |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — `app/Makefile`; marker `integration`, `req`. Không mypy/CI |

## Mục tiêu

Có khung `server/`, `web/`, `eval/`, `deploy/` và lệnh `make check` chạy được (dù chưa có logic), để mọi task sau có cùng cách chạy và kiểm tra.

## Đọc trước

- Blueprint §3.1.2 (cây thư mục), §3.3.3 (quy tắc kiểm tra)
- PLAN.md §3, §4
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `Makefile`, `.gitignore`, `.env.example`, `README.md` (phần phát triển)
- `server/pyproject.toml` (ruff, mypy, pytest, import-linter), `server/cwd_server/__init__.py`, `server/tests/`
- `web/` (Vite + React + TypeScript, vitest, eslint)
- `eval/`, `deploy/` (thư mục rỗng có README một dòng)

## Các bước

1. Kiểm tra phiên bản Python: máy hiện có `python3` 3.9.6, **không đủ** (mã dùng cú pháp `X | Y`). Cài và dùng Python ≥ 3.11 (ghi phiên bản trong `pyproject.toml`); Node ≥ 20.
2. Tạo cấu trúc như PLAN §4; package Python tên `cwd_server` nằm trong `server/`.
3. Đăng ký marker pytest `integration` (cần PostgreSQL/MinIO) và `req(id)` (gắn mã yêu cầu như `US-001-AC2` vào test; PLAN §2.4). Đặt `pytest -m 'not integration'` làm mặc định cho `make check`.
4. Viết `Makefile` với các đích: `setup`, `check` (ruff + mypy + pytest unit + `lint-imports` + web lint/typecheck/test), `test-int`, `up`, `down`, `migrate`, `e2e`. Thêm sẵn các đích giữ chỗ `contract`, `eval`, `trace`, `proxy-test`, `llm-smoke`; đích chưa có nội dung in “chưa triển khai” và thoát 0 (các task S3-04, S8-03, S8-04, S8-06, S8-10 sẽ điền).
5. Thêm một test mẫu cho server và một test mẫu cho web để `make check` có gì để chạy.

## Tiêu chí hoàn thành

- [ ] `make setup && make check` thoát mã 0 trên máy sạch.
- [ ] `pytest --markers` liệt kê `integration` và `req`.
- [ ] `git status` không có tệp sinh ra (venv, node_modules, __pycache__) nằm ngoài `.gitignore`.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Chưa viết logic nghiệp vụ.
- Chưa dựng Docker (S0-02).

## Ghi chú và rủi ro

- Đây là lựa chọn công nghệ `[Đề xuất]` (SAD §2.1–§2.3). Nếu Tech Lead đổi stack, sửa ở task này trước; các task sau chỉ tham chiếu qua `make`.
