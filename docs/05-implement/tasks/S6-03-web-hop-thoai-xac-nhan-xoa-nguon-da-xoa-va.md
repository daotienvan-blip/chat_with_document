# S6-03 — Web: hộp thoại xác nhận xóa, nguồn “(đã xóa)” và xử lý 404

| | |
|---|---|
| **Lát cắt** | S6 — Xóa tài liệu (UC12) (mốc M3) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Web |
| **Phụ thuộc** | [S1-04](S1-04-web-danh-sach-tai-lieu-huy-hieu-trang-thai.md), [S4-03](S4-03-web-nguon-dang-chip-va-mo-tai-lieu-nguon-o.md), [S6-01](S6-01-xoa-mem-documentservice-delete-api-delete.md) |
| **Truy vết** | UC12, UC17, US-005-AC1, EC-16 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Xóa mềm, purge đúng thứ tự, race, hộp thoại tiếp cận |

## Mục tiêu

Xóa có xác nhận đúng chuẩn tiếp cận; các nguồn cũ trong cuộc trao đổi tự đánh dấu “(đã xóa)”.

## Đọc trước

- html_design/scr-04-xac-nhan-xoa.html
- Blueprint §2.4 (Accessibility)
- API_Design §3.6.3
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `web/src/features/documents/{DeleteDialog,useDeleteDocument}.tsx`
- `web/src/features/sources/goneSources.ts`
- test tương ứng

## Các bước

1. Hộp thoại `role=alertdialog`, `aria-modal`, nhãn/mô tả; mở ⇒ focus vào **Hủy**; bẫy Tab; Esc = Hủy (trừ khi đang xóa); đóng ⇒ trả focus về nút xóa.
2. Ba trạng thái: mặc định, đang xóa (khóa nút, `role=status`), lỗi (`role=alert`, nút “Thử xóa lại”). `204` hoặc `404` ⇒ gỡ khỏi danh sách và đóng.
3. Đánh dấu nguồn đã xóa: tập `documentId` còn trong danh sách mới nhất; nguồn trong cuộc trao đổi mà `documentId` không còn ⇒ chip `gone`.
4. Nhắc người dùng rõ hệ quả (không hoàn tác, câu trả lời cũ giữ nguyên) đúng nội dung thiết kế; không hứa xóa bản sao lưu.

## Tiêu chí hoàn thành

- [ ] `make check` xanh; test gắn `req` US-005-AC1; test tiếp cận: focus ban đầu, bẫy Tab, Esc, trả focus.
- [ ] Test: `DELETE` trả `404` vẫn gỡ dòng; `503` hiện lỗi và giữ tài liệu.
- [ ] Test: sau khi xóa, chip nguồn tương ứng chuyển sang `gone` không cần tải lại trang.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Xóa hàng loạt.
