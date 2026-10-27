# S4-03 — Web: nguồn dạng chip và mở tài liệu nguồn ở thẻ mới đúng trang

| | |
|---|---|
| **Lát cắt** | S4 — Số trang và mở tài liệu nguồn (UC16, UC17) (mốc M2) |
| **Cỡ** | S (1–3 vòng lặp) |
| **Đường** | Web |
| **Phụ thuộc** | [S3-06](S3-06-web-khung-hoi-dap-trang-thai-cho-ba-loai.md), [S4-02](S4-02-api-get-documents-id-file-phat-pdf-range.md) |
| **Truy vết** | UC15, UC16, UC17, US-007-AC1, US-008-AC1 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | 🟡 Một phần (2026-10-27) — Chip nguồn + test. **Chưa thử tay `#page=N` trên trình duyệt** (OQ-P09) |

## Mục tiêu

Mỗi nguồn hiển thị ngay dưới câu trả lời, bấm vào mở PDF ở thẻ mới tại trang đầu tiên.

## Đọc trước

- html_design/scr-02-hoi-dap.html (.chip)
- API_Design §3.5.2 mục 6
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `web/src/features/sources/{SourceChip,SourceList}.tsx`
- test tương ứng

## Các bước

1. Chip: biểu tượng tệp + tên + “tr. 4, 5” + biểu tượng liên kết ngoài; là `<a target="_blank" rel="noopener">` tới `/api/v1/documents/{id}/file#page=<trang đầu>`; `aria-label` nêu rõ mở thẻ mới.
2. `pages` rỗng ⇒ chỉ tên, không `#page`.
3. Chip trạng thái `gone` (gạch đứt, “(đã xóa)”, không bấm được) — chỉ thành phần; logic đánh dấu ở S6-03.
4. Tên dài xuống dòng, không tràn.

## Tiêu chí hoàn thành

- [ ] `make check` xanh; test: URL đúng với một và nhiều trang, `rel` đúng, `aria-label`, chip `gone` không có `href`.
- [ ] Test gắn `req` US-007-AC1 (nguồn hiển thị ngay dưới câu trả lời).
- [ ] Kiểm tra tay với server thật: bấm chip mở PDF đúng trang trên trình duyệt đang dùng (ghi trình duyệt và kết quả; OQ-P09).
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Đánh dấu nguồn đã xóa tự động (S6-03).

## Ghi chú và rủi ro

- `#page=` do trình xem PDF của trình duyệt xử lý; hành vi có thể khác nhau giữa trình duyệt (API_Design §3.5.2).
