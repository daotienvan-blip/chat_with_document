# S0-03 — Nền tảng server: cấu hình, log, lỗi problem+json, /config và health

| | |
|---|---|
| **Lát cắt** | S0 — Khung chạy được (walking skeleton) (mốc M0) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S0-01](S0-01-khoi-tao-repo-cong-cu-va-quy-uoc-kiem-thu.md) |
| **Truy vết** | NFR-SEC (tiêu đề cơ bản) |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Cấu hình, log JSON, problem+json 12 mã, `/config`, `/healthz`, `/readyz` |

## Mục tiêu

Khởi động được ứng dụng FastAPI với cấu hình từ biến môi trường, mọi lỗi trả `application/problem+json` đúng `openapi.yaml`, và có `GET /api/v1/config`, `/healthz`, `/readyz` (bản tạm).

## Đọc trước

- API_Design §3.5.1, §3.5.3, §3.5.5
- openapi.yaml (Problem, Config)
- Blueprint §3.4.4 (khóa cấu hình)
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/cwd_server/platform/{config,logging,errors,request_id}.py`
- `server/cwd_server/api/{app,routers/config,routers/health}.py`
- `server/tests/unit/test_errors.py`, `test_config_endpoint.py`

## Các bước

1. `Settings` (pydantic-settings): `DATABASE_URL`, `S3_*`, `LLM_*`, `MAX_FILE_SIZE_MB` (có thể null), `MAX_QUESTION_LENGTH` (null), `LANGUAGE` (null), `POLL_INTERVAL_MS=2000`, các khóa `rag.*` theo Blueprint §3.4.4, `HARD_MAX_UPLOAD_MB` (mặc định `[Đề xuất]` 200, chống tải không giới hạn khi giới hạn nghiệp vụ còn null).
2. `AppError(code, status, detail, limit=None)` và một bảng ánh xạ `ProblemCode` → (HTTP, `type` dạng `urn:cwd:problem:<kebab>`, `title`, `detail` mặc định) đúng 12 mã trong `openapi.yaml`. Exception handler dựng JSON `application/problem+json` có `requestId`.
3. Middleware `X-Request-Id`: dùng giá trị proxy gắn nếu có, ngược lại sinh mới (dev); luôn đặt vào header phản hồi và ngữ cảnh log.
4. Log JSON có cấu trúc (`ts, level, service, requestId, event, durationMs, errorCode`). **Không** ghi thân yêu cầu/phản hồi.
5. Các endpoint: `GET /api/v1/config` (đúng schema `Config`, `Cache-Control: no-store`), `GET /healthz` (200), `GET /readyz` (tạm 200; S8-01 làm thật). Mọi lỗi 404/405/422 của framework cũng đi qua handler (`INVALID_REQUEST`/`NOT_FOUND`).

## Tiêu chí hoàn thành

- [ ] `make check` xanh; có test cho từng `ProblemCode` kiểm tra `Content-Type`, `status`, `code`, `requestId`.
- [ ] Test: lỗi không chứa stack trace, đường dẫn tệp hay tên thư viện.
- [ ] `curl -i localhost:8000/api/v1/config` trả `200` với các trường `null` khi chưa đặt biến môi trường, và có header `X-Request-Id`.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Chưa có CSDL (S0-04).
- Chưa có giới hạn tốc độ (S7-01).
- Chưa có `/metrics` (S8-01).

## Ghi chú và rủi ro

- Dùng endpoint đồng bộ (`def`) và SQLAlchemy đồng bộ ở mọi task sau (PLAN §3). Giữ `detail` tiếng Việt theo bảng ở API_Design §3.5.5.
