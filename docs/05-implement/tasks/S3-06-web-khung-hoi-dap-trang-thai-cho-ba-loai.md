# S3-06 — Web: khung hỏi đáp, trạng thái chờ, ba loại hiển thị cơ bản và sessionStorage

| | |
|---|---|
| **Lát cắt** | S3 — Hỏi đáp có nguồn: có căn cứ hoặc không tìm thấy (UC14, UC15, UC19, UC21) (mốc M2) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Web |
| **Phụ thuộc** | [S0-07](S0-07-khung-web-app-shell-token-thiet-ke-va-api.md), [S2-06](S2-06-web-ly-do-loi-thong-bao-san-sang-trang-thai.md) |
| **Truy vết** | UC14, UC19, US-006-AC1, US-006-AC3, US-007-AC1, US-010-AC1, EC-08, EC-09 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — xem IMPLEMENTATION_STATUS.md |

## Mục tiêu

Người dùng gửi câu hỏi và đọc câu trả lời có nguồn hoặc “không tìm thấy”; cuộc trao đổi giữ trong trình duyệt.

## Đọc trước

- html_design/scr-02-hoi-dap.html, scr-05-loi-he-thong.html
- Blueprint §3.7.3
- API_Design §3.6.2
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `web/src/features/chat/{Composer,ChatLog,AnswerCard,useAsk}.tsx`
- `web/src/state/conversation.ts` (sessionStorage có phiên bản lược đồ)
- test tương ứng

## Các bước

1. `Composer`: nhãn rõ ràng, Enter gửi / Shift+Enter xuống dòng, nút Gửi khóa khi rỗng (EC-08), bộ đếm ký tự, báo vượt giới hạn tại trường (`aria-invalid`).
2. `useAsk`: trạng thái `sending` (chỉ báo trong ≤ 300 ms, nút Hủy, `AbortController`, hết thời gian 45 s); thành công ⇒ thêm lượt vào cuộc trao đổi.
3. `AnswerCard` theo `status`: **answered** (nhãn “Có căn cứ”), **not_found** (nền xám, kính lúp, gợi ý đặt lại câu hỏi); `partial` hiển thị tạm như answered với nhãn “Trả lời một phần” (hoàn thiện ở S5-02). Nguồn hiển thị dạng danh sách chữ (chip ở S4-03).
4. `sessionStorage`: lưu/khôi phục, nút “Cuộc trao đổi mới” chỉ xóa phía trình duyệt. Lỗi: giữ nguyên câu hỏi và hiển thị thông báo chung có nút Gửi lại (ánh xạ chi tiết ở S7-03).

## Tiêu chí hoàn thành

- [ ] `make check` xanh; test gắn `req` US-006-AC1, US-010-AC1, EC-08 (không gửi khi rỗng).
- [ ] Test: tải lại trang giữ nguyên cuộc trao đổi; “Cuộc trao đổi mới” làm trống và khóa nút.
- [ ] Test: Hủy trong lúc chờ giữ lại câu hỏi và mở lại nút Gửi.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Chip nguồn (S4-03), hiển thị một phần chi tiết (S5-02), ánh xạ lỗi đầy đủ (S7-03).

## Ghi chú và rủi ro

- Mỗi câu hỏi độc lập: không gửi lịch sử lên máy chủ.
