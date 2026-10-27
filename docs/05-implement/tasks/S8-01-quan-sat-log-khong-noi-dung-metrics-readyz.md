# S8-01 — Quan sát: log không nội dung, /metrics, /readyz thật, requestId xuyên worker

| | |
|---|---|
| **Lát cắt** | S8 — Củng cố, vận hành và cổng phát hành (mốc M4) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S2-05](S2-05-worker-entrypoint-vong-quet-tat-em-va-kiem.md), [S3-05](S3-05-api-post-questions.md) |
| **Truy vết** | QAS-09, C-12, NFR-OBS |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — `/metrics`, `/readyz` thật, test canary không lộ nội dung. Không có OpenTelemetry (tùy chọn) |

## Mục tiêu

Chẩn đoán được sự cố bằng `requestId` mà không lộ nội dung; có số đo vận hành cho cảnh báo.

## Đọc trước

- SAD §4.3
- Blueprint §2.3 (QAS-09)
- Database_Design §6
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `platform/{metrics,logging}.py`, `api/routers/health.py`
- `worker/` (log, `request_id` từ `jobs`)
- `server/tests/integration/test_observability.py`

## Các bước

1. `/readyz`: kiểm tra `SELECT 1`, truy vấn bảng `jobs`, `head_bucket` kho; một thành phần lỗi ⇒ `503`.
2. `/metrics` (Prometheus): yêu cầu HTTP theo route/mã + độ trễ; số việc theo trạng thái, tuổi việc cũ nhất, thời lượng xử lý; lời gọi AI theo thao tác/kết quả + độ trễ; số câu trả lời theo `status`; số lần G-L2 hạ cấp; trạng thái breaker. Không dùng nhãn là tên tài liệu hay nội dung.
3. `jobs.request_id` được ghi lúc tải/xóa và dùng làm `requestId` trong log của worker.
4. Test “không lộ”: chạy trọn luồng với chuỗi canh (`CANARY-…`) trong câu hỏi, văn bản PDF, tên tệp; quét mọi log và `/metrics` đã bắt ⇒ không xuất hiện. (Tên tệp chỉ được ở nhãn khi cần: mặc định không.)

## Tiêu chí hoàn thành

- [ ] `make test-int` xanh gồm test canary.
- [ ] `curl /metrics` có các họ số đo nêu trên; `curl /readyz` trả `503` khi dừng PostgreSQL.
- [ ] 100% log mức lỗi trong test có `requestId`.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Trace OpenTelemetry (tùy chọn `[Đề xuất]`, làm sau nếu cần).
- Cảnh báo (cấu hình ở hệ thống giám sát).

## Ghi chú và rủi ro

- `/metrics` chỉ mở cho mạng hạ tầng — cấu hình ở proxy (S8-06).
