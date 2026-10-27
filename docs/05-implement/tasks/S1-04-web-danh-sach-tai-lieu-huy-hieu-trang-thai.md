# S1-04 — Web: danh sách tài liệu, huy hiệu trạng thái và polling

| | |
|---|---|
| **Lát cắt** | S1 — Tải PDF lên và xem danh sách (UC07, UC08, UC11) (mốc M1) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Web |
| **Phụ thuộc** | [S0-07](S0-07-khung-web-app-shell-token-thiet-ke-va-api.md) |
| **Truy vết** | UC11, UC09, US-004-AC1, US-002-AC2 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Kiểm tra tệp, tải lên nguyên tử + bù trừ, API, danh sách + polling, tải lên có tiến độ/hủy/thử lại |

## Mục tiêu

Panel “Tài liệu” hiển thị danh sách và trạng thái từ `GET /documents`, tự cập nhật khi còn tài liệu đang xử lý.

## Đọc trước

- html_design/scr-02-hoi-dap.html, scr-03-tai-len.html
- API_Design §3.7.3 (quy tắc polling)
- Blueprint §3.7.4
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `web/src/features/documents/{DocumentList,DocumentRow,StatusBadge}.tsx`, `useDocuments.ts`
- `web/src/features/documents/*.test.tsx` (MSW)

## Các bước

1. `StatusBadge`: Sẵn sàng / Đang xử lý / Lỗi — luôn có biểu tượng **và** chữ (không chỉ màu).
2. `DocumentRow`: tên (cắt dài, `title`), kích thước, số trang, huy hiệu, vùng thông báo lỗi (nội dung ở S2-06).
3. `useDocuments`: TanStack Query; **chỉ poll khi còn ≥ 1 `processing`** theo `pollIntervalMs`; tăng gấp đôi (tối đa 30 s) sau `429/503` và tôn trọng `Retry-After`; tạm dừng khi `document.hidden`.
4. Trạng thái trống và trạng thái đang tải (khung xương), lỗi tải danh sách có nút thử lại.

## Tiêu chí hoàn thành

- [ ] `make check` xanh.
- [ ] Test: dừng poll khi không còn `processing` (đếm số lần gọi); tăng khoảng cách sau 503; hiển thị đúng 3 huy hiệu với chữ.
- [ ] Quan sát tay với server thật nếu đã có S1-03.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Tải lên (S1-05), xóa (S6-03), nội dung lý do lỗi (S2-06).

## Ghi chú và rủi ro

- Có thể làm song song với backend vì dùng MSW theo `openapi.yaml`.
