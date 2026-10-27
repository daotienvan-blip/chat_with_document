# S7-03 — Web: xử lý lỗi hỏi đáp theo SCR-05 (thử lại, đếm ngược, mất mạng, hết thời gian)

| | |
|---|---|
| **Lát cắt** | S7 — Chịu lỗi và quá tải (mốc M4) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Web |
| **Phụ thuộc** | [S3-06](S3-06-web-khung-hoi-dap-trang-thai-cho-ba-loai.md) |
| **Truy vết** | UC14, EC-07, EC-09, EC-15, A-09 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — LoadGuard + rate limit; retry + breaker; lỗi UI + đếm ngược; đối soát |

## Mục tiêu

Mọi mã lỗi hỏi đáp có hành vi UI định nghĩa; người dùng không bao giờ mất câu hỏi đã nhập.

## Đọc trước

- html_design/scr-05-loi-he-thong.html
- API_Design §3.5.5
- Blueprint §3.5.4, §3.7.3
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `web/src/api-client/uiErrors.ts` (mã → thông báo, retryable, hành động)
- `web/src/features/chat/{ErrorTurn,useCountdown}.tsx`
- test tương ứng

## Các bước

1. Bảng ánh xạ cho `AI_UNAVAILABLE`, `AI_TIMEOUT`, `SYSTEM_BUSY`, `RATE_LIMITED`, `INTERNAL_ERROR`, `NETWORK`, `QUESTION_TOO_LONG`; mã lạ ⇒ lỗi chung (tương thích khi máy chủ thêm mã).
2. `RATE_LIMITED`/`SYSTEM_BUSY`: nút “Gửi lại sau N giây” đếm ngược theo `Retry-After` rồi tự mở.
3. `INTERNAL_ERROR`: hiển thị `requestId`. `QUESTION_TOO_LONG`: lỗi tại trường, `aria-invalid`, không gửi.
4. Mọi lỗi đặt `role=alert`; câu hỏi nguyên vẹn trong ô nhập.

## Tiêu chí hoàn thành

- [ ] `make check` xanh; một test cho từng mã (hiển thị đúng chữ, có/không có Gửi lại, ô nhập giữ nguyên).
- [ ] Test đếm ngược dùng đồng hồ giả.
- [ ] Test: mã lỗi không biết ⇒ thông báo chung, không vỡ giao diện.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Lỗi tải lên (S1-05).
