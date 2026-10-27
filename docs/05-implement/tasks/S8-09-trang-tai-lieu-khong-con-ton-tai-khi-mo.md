# S8-09 — Trang “Tài liệu không còn tồn tại” khi mở nguồn đã xóa (SCR-06)

| | |
|---|---|
| **Lát cắt** | S8 — Củng cố, vận hành và cổng phát hành (mốc M4) |
| **Cỡ** | S (1–3 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S4-02](S4-02-api-get-documents-id-file-phat-pdf-range.md), [S0-07](S0-07-khung-web-app-shell-token-thiet-ke-va-api.md) |
| **Truy vết** | UC17, EC-16, OQ-A02 |
| **Bị chặn bởi** | OQ-A02 |
| **Trạng thái** | ⛔ Chưa làm / bị chặn — Bị chặn OQ-A02 |

## Mục tiêu

Khi điều hướng trình duyệt tới `/file` của tài liệu đã xóa, người dùng thấy trang đầy đủ thay vì JSON thô.

## Đọc trước

- html_design/scr-06-nguon-da-xoa.html
- API_Design §6 (OQ-A02)
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `api/routers/files.py` (thương lượng `Accept`)
- `api/templates/document_gone.html` (sinh từ `html_design/scr-06`)
- cập nhật `openapi.yaml` (mô tả) và `API_Design.md` §3.5.2 mục 6

## Các bước

1. Nếu `Accept` ưu tiên `text/html` ⇒ trả `404` với trang HTML (kèm `requestId`); ngược lại `404 problem+json`. Đặt `Vary: Accept`.
2. Trang không dùng tài nguyên ngoài; nút “Đóng thẻ này” và liên kết về màn hình làm việc.
3. Cập nhật tài liệu thiết kế cùng lúc.

## Tiêu chí hoàn thành

- [ ] Test: `Accept: text/html` ⇒ `404` HTML; `Accept: application/json` ⇒ `404 problem+json`.
- [ ] `make contract` vẫn xanh (đặc tả đã cập nhật).
- [ ] Kiểm tra tay: bấm chip nguồn của tài liệu vừa xóa ở tab khác ⇒ thấy trang thân thiện.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- (không có điều gì đặc biệt; không mở rộng sang việc của task khác)

## Ghi chú và rủi ro

- Chỉ làm khi OQ-A02 được chấp thuận.
