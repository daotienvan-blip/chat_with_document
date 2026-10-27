# S5-02 — Web: hiển thị trả lời một phần và nhiều nguồn

| | |
|---|---|
| **Lát cắt** | S5 — Tổng hợp nhiều tài liệu và trả lời một phần (UC18, UC19) (mốc M3) |
| **Cỡ** | S (1–3 vòng lặp) |
| **Đường** | Web |
| **Phụ thuộc** | [S4-03](S4-03-web-nguon-dang-chip-va-mo-tai-lieu-nguon-o.md), [S5-01](S5-01-backend-tong-hop-nhieu-tai-lieu-mau-thuan.md) |
| **Truy vết** | UC18, UC19, US-009-AC1, US-009-AC2, US-010-AC2 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — OQ-A03 (trường `missing`) chưa quyết định ⇒ không đổi hợp đồng |

## Mục tiêu

Ba loại phản hồi khác nhau rõ ràng (chữ, biểu tượng, viền, nền) và nhiều chip nguồn cho câu trả lời tổng hợp.

## Đọc trước

- html_design/scr-02-hoi-dap.html (a--partial, .missing)
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `web/src/features/chat/AnswerCard.tsx`, `MissingNote.tsx`
- test tương ứng

## Các bước

1. `partial`: nhãn “Trả lời một phần” (biểu tượng nửa vòng, viền vàng) + ghi chú cố định “Một phần câu hỏi không có trong tài liệu” cạnh câu trả lời. Nếu OQ-A03 đã được chấp thuận: tách khối “Không tìm thấy:” từ trường `missing`.
2. Nhiều nguồn: mỗi tài liệu một chip; mâu thuẫn hiển thị trong thân `answer` như nhận được.
3. Kiểm tra ba loại khác nhau không chỉ bằng màu (test truy vấn theo nhãn chữ và biểu tượng).

## Tiêu chí hoàn thành

- [ ] `make check` xanh; test gắn `req` US-010-AC2 và US-009-AC1 (liệt kê từng nguồn).
- [ ] So sánh trực quan với `html_design/scr-02-hoi-dap.html` (ghi trong PR).
- [ ] Không dùng `dangerouslySetInnerHTML`: nội dung câu trả lời render dạng chữ.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- (không có điều gì đặc biệt; không mở rộng sang việc của task khác)

## Ghi chú và rủi ro

- Văn bản LLM luôn được escape (SAD §4.1).
