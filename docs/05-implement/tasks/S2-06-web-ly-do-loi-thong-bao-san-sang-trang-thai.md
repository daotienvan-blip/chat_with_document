# S2-06 — Web: lý do lỗi, thông báo sẵn sàng, trạng thái trống và khóa khung hỏi

| | |
|---|---|
| **Lát cắt** | S2 — Xử lý tài liệu đến khi sẵn sàng hoặc lỗi (UC09, UC10) (mốc M1) |
| **Cỡ** | S (1–3 vòng lặp) |
| **Đường** | Web |
| **Phụ thuộc** | [S1-04](S1-04-web-danh-sach-tai-lieu-huy-hieu-trang-thai.md) |
| **Truy vết** | UC09, UC10, US-002-AC1, US-002-AC2, US-003-AC1, US-003-AC2, US-003-AC3, US-006-AC2, EC-01 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Lý do lỗi, thông báo sẵn sàng, khóa khung hỏi |

## Mục tiêu

Dòng tài liệu hiển thị đúng lý do lỗi kèm hướng xử lý; màn hình trống hướng dẫn tải; khung hỏi chỉ mở khi có tài liệu sẵn sàng.

## Đọc trước

- html_design/scr-01-man-hinh-chinh-trong.html, scr-03-tai-len.html
- API_Design §3.5.5
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `web/src/features/documents/failureMessages.ts`, `DocumentRow.tsx`
- `web/src/features/chat/useChatGate.ts`, `EmptyState.tsx`
- test tương ứng

## Các bước

1. Bảng 4 `failureReason` → (thông báo, gợi ý) lấy đúng từ API_Design/Blueprint §3.5.4, hiển thị `role=alert` trong dòng.
2. Khi một tài liệu chuyển `processing → ready` (qua polling) hiển thị thông báo `role=status` “đã sẵn sàng” gắn tên tài liệu.
3. `useChatGate`: có ≥ 1 tài liệu `ready` thì mở khung hỏi, ngược lại khóa và hiển thị hướng dẫn (EC-01); tự mở lại không cần tải trang.
4. Tài liệu chưa `ready` có chú thích “chưa dùng để trả lời” (US-002-AC2).

## Tiêu chí hoàn thành

- [ ] `make check` xanh; test có `req`: US-002-AC1, US-002-AC2, US-003-AC1/2/3, US-006-AC2.
- [ ] Test: khi danh sách chuyển từ rỗng sang có một `ready`, khung hỏi từ khóa sang mở.
- [ ] Không dùng chỉ màu để phân biệt trạng thái.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Khung hỏi đầy đủ (S3-06).
