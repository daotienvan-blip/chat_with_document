# S1-05 — Web: tải lên (chọn tệp, kéo thả, tiến độ, hủy, từ chối, thử lại)

| | |
|---|---|
| **Lát cắt** | S1 — Tải PDF lên và xem danh sách (UC07, UC08, UC11) (mốc M1) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Web |
| **Phụ thuộc** | [S1-04](S1-04-web-danh-sach-tai-lieu-huy-hieu-trang-thai.md) |
| **Truy vết** | UC07, UC08, US-001-AC1, US-001-AC2, US-001-AC3, US-003-AC4 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Kiểm tra tệp, tải lên nguyên tử + bù trừ, API, danh sách + polling, tải lên có tiến độ/hủy/thử lại |

## Mục tiêu

Người dùng tải được PDF với phản hồi rõ ràng ở mọi nhánh; tệp bị từ chối không tạo dòng trong danh sách.

## Đọc trước

- html_design/scr-03-tai-len.html
- Blueprint §3.7.4 (máy trạng thái tải lên)
- API_Design §3.5.5
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `web/src/features/documents/{UploadZone,useUpload}.tsx`, `uploadXhr.ts`
- test tương ứng

## Các bước

1. Nút “Tải PDF lên” là `<button>` mở hộp chọn tệp; vùng kéo thả không làm trình duyệt rời trang.
2. Kiểm tra trước ở client (đuôi `.pdf`; kích thước nếu `maxFileSizeMb` khác null); máy chủ vẫn là nguồn quyết định.
3. Gửi bằng `XMLHttpRequest` để có tiến độ (`fetch` không có); hủy bằng `abort()`; dòng tạm hiển thị thanh tiến độ `role=progressbar` + nút Hủy.
4. Ánh xạ lỗi: `UNSUPPORTED_TYPE`, `FILE_TOO_LARGE` → thông báo `role=alert` dưới vùng tải, không tạo dòng; lỗi mạng/`STORAGE_UNAVAILABLE`/5xx → dòng tạm “chưa tải được” với **Thử lại**; `202` → làm mới danh sách.

## Tiêu chí hoàn thành

- [ ] `make check` xanh.
- [ ] Test (gắn `req`): AC1 thành công; AC2 và AC3 hiển thị đúng thông báo và không thêm dòng; US-003-AC4 mất mạng rồi thử lại thành công, danh sách không có dòng “nửa vời”.
- [ ] Kiểm tra tay bằng bàn phím: Tab tới nút, Enter mở hộp chọn tệp.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Tải nhiều tệp cùng lúc (mỗi lần một tệp).
- Chống trùng (OQ-014).

## Ghi chú và rủi ro

- Nội dung thông báo lấy đúng từ API_Design §3.5.5; không tự nghĩ lại câu chữ.
