# Runbook — "Chat với tài liệu" (bản demo cục bộ)

> Mọi lệnh chạy trong `app/`. Stack kiểu sản xuất (Docker/nginx) đã chạy thử cục bộ trên Colima — mục “Stack kiểu sản xuất” bên dưới; chưa triển khai lên hạ tầng thật (OQ-005).

## Stack kiểu sản xuất (Docker, cục bộ)

| Việc | Lệnh |
|---|---|
| Cài (lần đầu) | `brew install colima docker docker-compose` |
| Dev: PostgreSQL (5433) + S3 (9000) | `make up` / `make down` |
| Build + chạy api×2, worker, proxy, CSDL, S3 | `make prod-up` → https://localhost:8443 (chứng chỉ tự ký ở `var/prod-local/certs/`) |
| Trạng thái | `make prod-ps` |
| Kiểm proxy (S8-06) | `make proxy-test` |
| Thử nâng cấp cuốn chiếu (S8-05) | `deploy/prod-local/rolling-test.sh <id tài liệu PDF lớn đã ready>` |
| Nâng cấp một bản api | `docker stop -t 50 cwd-prod-api-1` (uvicorn chờ yêu cầu đang chạy tối đa 45 s) → cập nhật → `docker start cwd-prod-api-1`, chờ healthy rồi làm bản kế |
| Dừng và **xóa dữ liệu** stack | `make prod-down` (xóa volume `prod-pgdata`, `prod-s3data`) |

Bí mật của stack cục bộ sinh ngẫu nhiên vào `var/prod-local/compose.env` (quyền 600, không commit). Sản xuất thật: lấy từ bộ quản lý bí mật, xem `deploy/env.prod.example`.

## Khởi động / dừng

| Việc | Lệnh |
|---|---|
| Cài phụ thuộc (lần đầu) | `make setup` (cần `brew install python@3.12 node postgresql@17 pgvector`) |
| Bật PostgreSQL | `make db-up` (dùng `pg_ctl`, không đăng ký tự khởi động) |
| Migration | `make migrate` |
| Chạy API + worker | `make run` → http://localhost:8000 (API phục vụ luôn giao diện đã build) |
| Dừng (tắt êm) | `make stop` |
| Toàn bộ demo | `make demo` (build web, sinh PDF minh họa, chạy, kiểm tra khói) |
| Xem log | `make logs` (JSON; không có nội dung câu hỏi/tài liệu) |
| Tắt PostgreSQL | `make db-down` |

## Kiểm tra

`make check` (lint, hợp đồng phụ thuộc, unit server, typecheck + test web) · `make test-int` (tích hợp trên PostgreSQL, gồm kiểm tra theo OpenAPI và phân quyền) · `make smoke` (đầu-cuối trên hệ thống đang chạy) · `make eval` (chất lượng AI) · `make trace` (phủ AC).

## Sự cố

| Tình huống | Làm gì |
|---|---|
| `readyz` trả 503 | `make db-up`; kiểm tra quyền ghi `app/var/storage`; xem `var/log/api.log` |
| Tài liệu kẹt ở “Đang xử lý” | Kiểm tra worker còn chạy (`var/run/worker.pid`); việc quá hạn khóa tự quay về hàng đợi sau ≤ 10 phút (vòng quét 5 phút) |
| Dịch vụ AI ngưng (`AI_UNAVAILABLE`) | Breaker mở 30 s rồi thử lại; worker hoãn việc mà không mất lần thử. Không cần thao tác nếu dịch vụ tự hồi phục |
| **Xóa khẩn cấp tài liệu nhạy cảm** | Xóa trên giao diện hoặc `curl -X DELETE localhost:8000/api/v1/documents/<id>` → loại khỏi tra cứu ngay. Muốn xóa vật lý ngay: đặt `PURGE_DELAY_S=0` rồi xóa, hoặc chờ ≤ 1 giờ. **Dữ liệu còn trong bản sao lưu tới 7 ngày** (OQ-D01) — xóa bản sao lưu liên quan nếu chính sách yêu cầu |
| Lệch CSDL ↔ kho tệp | Đối soát chạy mỗi giờ trong worker (tệp mồ côi > 24 giờ bị xóa; tài liệu mất tệp → `PROCESSING_ERROR`) |

## Sao lưu / khôi phục

- Sao lưu: `deploy/backup.sh cwd` → `var/backups/cwd-<thời gian>.dump` (giữ 7 bản). PDF gốc: sao lưu `var/storage/` (sản xuất: versioning bucket).
- Khôi phục: `deploy/restore.sh <tệp.dump> cwd` (tạo lại CSDL rồi đối soát).
- **Khôi phục thử 2026-10-27:** dump CSDL demo → khôi phục sang `cwd_restore_drill` → 4/3 (tài liệu/đoạn) trước và sau khớp; đối soát `{orphans_deleted: 0, missing_files: 0, requeued: 0}`.

## Thay đổi cấu hình thường gặp (`app/.env`)

| Biến | Ý nghĩa |
|---|---|
| `MAX_FILE_SIZE_MB`, `MAX_QUESTION_LENGTH` | Giới hạn nghiệp vụ `[TBD: OQ-009, OQ-P06]`; để trống = chưa quyết định |
| `LLM_PROVIDER=http` + `LLM_*` | Bật AI thật (tương thích OpenAI) — **chỉ khi OQ-005 cho phép**; đặt `EMBEDDING_DIM` đúng mô hình |
| `RETRIEVAL_MODE` | `exact` (mặc định, theo spike S3-00) hoặc `hnsw` |

## Đổi mô hình embedding

`EMBEDDING_DIM` đổi ⇒ cột `chunks.embedding` không dùng lại được. Với demo: `make stop`, xóa dữ liệu (`TRUNCATE jobs, chunks, documents` + `var/storage`), tạo lại lược đồ, tải lại tài liệu. Với sản xuất: theo Database_Design §5.3 (thêm cột mới, dựng lại đoạn, chuyển truy xuất, bỏ cột cũ).
