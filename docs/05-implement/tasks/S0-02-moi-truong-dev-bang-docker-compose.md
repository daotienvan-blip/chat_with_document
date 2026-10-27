# S0-02 — Môi trường dev bằng Docker Compose (PostgreSQL + pgvector, MinIO)

| | |
|---|---|
| **Lát cắt** | S0 — Khung chạy được (walking skeleton) (mốc M0) |
| **Cỡ** | S (1–3 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S0-01](S0-01-khoi-tao-repo-cong-cu-va-quy-uoc-kiem-thu.md) |
| **Truy vết** | — |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — `make up` trên Colima: PostgreSQL 17.11 + pgvector 0.8.7 (cổng 5433), S3 = SeaweedFS 4.50 (cổng 9000) thay MinIO (ảnh MinIO không còn phát hành công khai) |

## Mục tiêu

`make up` dựng PostgreSQL có tiện ích `vector` và một object storage tương thích S3 (MinIO) cùng bucket, để chạy kiểm thử tích hợp cục bộ.

## Đọc trước

- SAD §5.1
- Database_Design §3.5.2
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `deploy/compose.dev.yaml`
- `.env.example` (thêm biến kết nối)
- `deploy/dev/init-bucket.sh` hoặc dịch vụ khởi tạo bucket

## Các bước

1. Dịch vụ `postgres`: ảnh có pgvector, tạo hai CSDL `cwd` và `cwd_test`, healthcheck `pg_isready`.
2. Dịch vụ `minio` + bước tạo bucket `cwd-documents` (private).
3. Bật `shared_buffers`, `maintenance_work_mem` theo Database_Design §3.5.2 qua tham số lệnh (không bắt buộc ở dev).
4. Cập nhật `make up/down` và ghi `DATABASE_URL`, `TEST_DATABASE_URL`, `S3_ENDPOINT`… vào `.env.example`.

## Tiêu chí hoàn thành

- [x] `make up` xong, `docker compose ps` cho thấy các dịch vụ `healthy`.
- [x] `psql $DATABASE_URL -c "CREATE EXTENSION IF NOT EXISTS vector"` thành công.
- [x] Dùng client S3 (mc/aws cli) tải lên và liệt kê được một đối tượng thử trong bucket, rồi xóa.
- [x] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Không dựng `api`/`worker`/proxy ở đây (S2-05, S8-05).
- Chưa có vai trò CSDL tối thiểu (S8-02).

## Ghi chú và rủi ro

- Chọn ảnh pgvector có hỗ trợ HNSW; ghi phiên bản đã dùng vào README (rủi ro ở Database_Design §3.4.5).

## Kết quả chạy (2026-10-27)

- Môi trường: Colima 2 CPU / 3 GB, Docker 29.5.2, Compose 5.6.1 (cài bằng Homebrew).
- `make up`: `postgres` và `s3` **healthy**; `s3-init` tạo bucket `cwd-documents`, bật versioning và lifecycle (xóa phiên bản cũ sau 7 ngày, OQ-D01). Chạy lại lần 2 không lỗi.
- `CREATE EXTENSION vector` thành công trên `cwd` và `cwd_test` (pgvector 0.8.7); `shared_buffers=1GB`, `maintenance_work_mem=256MB`.
- aws-cli: tải lên → liệt kê → xóa một đối tượng thử thành công.
- `make check` xanh; 28/28 test tích hợp xanh trên PostgreSQL Docker (`TEST_DATABASE_URL=…:5433/cwd_test`) và trên PostgreSQL Homebrew.
- Thêm: chạy api+worker với `OBJECT_STORE=s3` trỏ vào stack này, `smoke.py` 17/17; purge xóa đúng tệp trên S3.
- **Khác kế hoạch:** MinIO → SeaweedFS (`minio/minio`, `quay.io/minio/*`, `bitnami/minio` đều không pull được). Cổng PostgreSQL 5433 để chạy song song bản demo Homebrew (5432).
- **Chưa kiểm chứng:** lifecycle 7 ngày thực sự xóa phiên bản cũ (chỉ xác nhận quy tắc được lưu).
