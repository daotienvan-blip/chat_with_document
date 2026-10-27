# S8-03 — Bộ kiểm thử hợp đồng theo openapi.yaml

| | |
|---|---|
| **Lát cắt** | S8 — Củng cố, vận hành và cổng phát hành (mốc M4) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S3-05](S3-05-api-post-questions.md), [S4-02](S4-02-api-get-documents-id-file-phat-pdf-range.md), [S6-01](S6-01-xoa-mem-documentservice-delete-api-delete.md) |
| **Truy vết** | A-05, A-10, NFR-API |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | 🟡 Một phần (2026-10-27) — Phản hồi trong mọi test tích hợp được kiểm theo OpenAPI; **chưa có bộ duyệt hệ thống mọi thao tác × mã** hay Schemathesis |

## Mục tiêu

Mọi thao tác và mã lỗi trong OpenAPI được kiểm tự động trên ứng dụng thật (dữ liệu giả), kể cả bất biến `Answer` và việc không lộ thông tin trong lỗi.

## Đọc trước

- openapi.yaml
- API_Design §4.3
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/tests/contract/*`
- `make contract`

## Các bước

1. Duyệt `openapi.yaml`: với mỗi thao tác và mỗi mã phản hồi được khai báo có ví dụ yêu cầu gây ra nó; xác nhận trạng thái, header khai báo và thân khớp schema.
2. Bất biến `Answer` tham số hóa cho ba `status`; kiểm tra lỗi không chứa stack, đường dẫn, SQL, tên nhà cung cấp AI, khóa lưu trữ.
3. Tùy chọn: chạy một công cụ kiểm thử theo đặc tả (kiểu Schemathesis) ở chế độ smoke với `FakeLlm`; không `5xx` với đầu vào hợp lệ theo schema.
4. Một test kiểm tra `openapi.yaml` hợp lệ OpenAPI 3.0 và `web/src/api-client/generated.ts` không lệch (S0-07).

## Tiêu chí hoàn thành

- [ ] `make contract` xanh; báo cáo liệt kê số thao tác × mã phản hồi đã phủ (mục tiêu: 100% mã có trong spec ngoại trừ `INTERNAL_ERROR` được mô phỏng).
- [ ] Cố ý đổi tên một trường trong router ⇒ `make contract` thất bại (kiểm tra tay rồi hoàn lại).
- [ ] Đã gắn vào CI.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- (không có điều gì đặc biệt; không mở rộng sang việc của task khác)
