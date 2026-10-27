# Phỏng vấn elicitation — Chat với tài liệu (MVP)

> **Trạng thái tổng:** **Chưa có buổi phỏng vấn nào.** Các file ở đây là bộ câu hỏi chuẩn bị. Prompt elicitation `BRD_Elicitation_Prompt_IEEE_standard.md` không có trong máy (xem `docs/01-intake/sources.md`); bộ câu hỏi lấy từ các câu hỏi mở của BRD §12 và PRD §7.
> **Phạm vi:** chỉ giữ hai nhóm gắn trực tiếp với use case của `use-case-diagram.drawio`: người dùng kinh doanh (actor duy nhất) và business owner (xác nhận ngưỡng chất lượng). Các nhóm không phải actor (sponsor, CNTT/bảo mật, chủ sở hữu tài liệu) không có bộ câu hỏi riêng; OQ-005, OQ-007 cần được hỏi trực tiếp khi có cuộc họp.

| File | Đối tượng | Câu hỏi mở chính | Trạng thái |
|---|---|---|---|
| `02-nguoi-dung-kinh-doanh.md` | Người dùng kinh doanh (STK-001, STK-005) | OQ-001, 008, 011, P02, P05, P07 | Chưa phỏng vấn |
| `03-business-owner.md` | Business owner | OQ-004, 011, 014 | Chưa phỏng vấn |

Số hiệu file giữ nguyên (không đánh số lại sau khi xóa 01, 04, 05).

## Thứ tự ưu tiên

1. Business owner trước, để có ngưỡng chính xác và bộ câu hỏi kiểm thử (OQ-004).
2. Người dùng sau, kèm quan sát một lượt tra cứu thật.

## Quy trình sau mỗi buổi

1. Điền cột "Trả lời" và ghi chú cuối file, giữ nguyên văn câu trả lời.
2. Cập nhật OQ tương ứng trong BRD §12 (Trạng thái, Kết quả) và các giá trị `[TBD]` liên quan.
3. Cập nhật PRD, SDD, SADD, UIUX nếu kết quả đổi phạm vi.
4. Ghi ngày phỏng vấn và người tham dự vào file.
