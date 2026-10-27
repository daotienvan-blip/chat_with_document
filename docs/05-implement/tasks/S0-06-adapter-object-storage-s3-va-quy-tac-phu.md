# S0-06 — Adapter object storage S3 và quy tắc phụ thuộc tự động

| | |
|---|---|
| **Lát cắt** | S0 — Khung chạy được (walking skeleton) (mốc M0) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S0-02](S0-02-moi-truong-dev-bang-docker-compose.md), [S0-05](S0-05-kieu-mien-cong-ports-adapter-gia-va.md) |
| **Truy vết** | QAS-06, BR-016 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — `tests/integration/test_s3_store.py` 2/2 trên SeaweedFS; sửa lỗi `check()` ném `FileNotFoundError` khi thiếu bucket; thử vi phạm import → import-linter BROKEN |

## Mục tiêu

`ObjectStorePort` chạy được với MinIO/S3 thật và CI chặn mã vi phạm ma trận phụ thuộc.

## Đọc trước

- Blueprint §3.3.1, §3.3.3
- SAD §4.1 (khóa lưu trữ)
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/cwd_server/adapters/s3_store.py`
- `server/.importlinter` (hoặc mục trong `pyproject.toml`)
- `server/tests/integration/test_s3_store.py`

## Các bước

1. Cài đặt `put/get(range)/delete/list_keys` bằng boto3; lỗi kết nối/5xx → `StorageUnavailable`; `delete` khóa không tồn tại không lỗi.
2. Khóa chỉ dạng `documents/{uuid}.pdf`; adapter từ chối khóa sai dạng (chống path traversal).
3. Cấu hình import-linter theo ma trận Blueprint §3.3.1: `core` không import `adapters`/`persistence`/`api`; chỉ `adapters/s3_store` được import boto3; chỉ `adapters/llm_*` được import SDK AI. Gắn vào `make check`.
4. Test tích hợp với MinIO: put → get toàn bộ → get range → list → delete → get báo không tồn tại.

## Tiêu chí hoàn thành

- [x] `make test-int` xanh phần S3.
- [x] Cố ý thêm `import cwd_server.adapters` vào `core/` → `make check` **thất bại** (kiểm tra thủ công rồi hoàn lại).
- [x] Test: khóa `../x.pdf` bị từ chối.
- [x] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Chưa dùng trong luồng tải lên (S1-02).

## Ghi chú và rủi ro

- Mã hóa phía máy chủ và vị trí lưu trữ do cấu hình bucket/nền tảng (S8-07), không phải adapter.
