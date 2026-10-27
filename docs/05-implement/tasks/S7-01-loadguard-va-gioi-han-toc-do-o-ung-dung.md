# S7-01 — LoadGuard và giới hạn tốc độ ở ứng dụng

| | |
|---|---|
| **Lát cắt** | S7 — Chịu lỗi và quá tải (mốc M4) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S3-05](S3-05-api-post-questions.md), [S1-03](S1-03-api-tai-lieu-post-documents-get-documents.md) |
| **Truy vết** | NFR-SCL-002, QAS-02, A-09, C-13 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — LoadGuard + rate limit; retry + breaker; lỗi UI + đếm ngược; đối soát |

## Mục tiêu

Quá tải/quá nhanh trả `SYSTEM_BUSY`/`RATE_LIMITED` có `Retry-After`, không treo và không làm mất tài liệu.

## Đọc trước

- API_Design §3.8.2
- SAD §4.1 (Chống lạm dụng), §4.2 (Quá tải)
- Blueprint §3.8.2
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `core/guard/load_guard.py`, `api/middleware/rate_limit.py`
- `server/tests/unit/test_{load_guard,rate_limit}.py`

## Các bước

1. `LoadGuard(max_concurrent=8, wait_seconds=2)`: semaphore theo tiến trình `api`; hết chỗ sau 2 s ⇒ `SystemBusy` (503, `Retry-After`). Áp dụng cho `POST /questions` và (mức riêng, mặc định 4) `POST /documents`.
2. Token bucket theo khóa khách (địa chỉ nguồn; dùng `X-Forwarded-For` đầu tiên **chỉ khi** `TRUST_PROXY=true`): `POST /questions` 30/phút, `POST /documents` 10/phút, còn lại 120/phút; vượt ⇒ `429 RATE_LIMITED` + `Retry-After`. Tất cả cấu hình được và tắt được (proxy ở S8-06 cũng giới hạn, tránh đếm đôi).
3. Đồng hồ tiêm được để kiểm thử không phải ngủ.

## Tiêu chí hoàn thành

- [ ] `make check` xanh: 9 yêu cầu đồng thời với giới hạn 8 ⇒ đúng 1 yêu cầu nhận `SYSTEM_BUSY` sau 2 s; vượt 30/phút ⇒ `429` kèm `Retry-After` đúng; cửa sổ trượt khôi phục.
- [ ] Test: quá tải không làm thay đổi số tài liệu (NFR-SCL-002).
- [ ] Phản hồi lỗi qua `assert_matches_openapi`.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Giới hạn ở proxy (S8-06).

## Ghi chú và rủi ro

- Rủi ro NAT/VPN dùng chung địa chỉ: xem API_Design §3.8.2; đây là lý do mọi hạn mức là cấu hình.
