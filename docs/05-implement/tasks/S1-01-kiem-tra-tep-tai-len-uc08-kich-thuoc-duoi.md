# S1-01 — Kiểm tra tệp tải lên (UC08): kích thước, đuôi, chữ ký %PDF-, băm, tên

| | |
|---|---|
| **Lát cắt** | S1 — Tải PDF lên và xem danh sách (UC07, UC08, UC11) (mốc M1) |
| **Cỡ** | S (1–3 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S0-05](S0-05-kieu-mien-cong-ports-adapter-gia-va.md) |
| **Truy vết** | UC08, US-001-AC2, US-001-AC3, BR-005, BRU-003, NFR-CAP-001 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Kiểm tra tệp, tải lên nguyên tử + bù trừ, API, danh sách + polling, tải lên có tiến độ/hủy/thử lại |

## Mục tiêu

Hàm thuần kiểm tra luồng tải lên theo thứ tự quy định, tính SHA-256 và làm sạch tên, không đọc quá giới hạn vào bộ nhớ.

## Đọc trước

- API_Design §3.5.2 mục 2
- Blueprint §3.2.3
- SAD §4.1 (Xác thực tệp)
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/cwd_server/core/documents/validate_upload.py`
- `server/tests/unit/test_validate_upload.py`

## Các bước

1. `validate_upload(stream, filename, max_bytes) -> ValidatedUpload(name, size, sha256, spooled_file)`: đọc theo khối, đếm byte, dừng và ném `FileTooLarge(limit_mb)` khi vượt; lưu vào `SpooledTemporaryFile` (vượt 8 MB ghi đĩa) để tải lên kho sau.
2. Thứ tự lỗi: thiếu tệp (`INVALID_REQUEST`) → quá lớn → sai đuôi `.pdf` (không phân biệt hoa/thường) hoặc 5 byte đầu ≠ `%PDF-` (`UnsupportedType`). **Không** tin `Content-Type`.
3. Làm sạch tên: chuẩn hóa NFC, bỏ ký tự điều khiển và dấu phân cách đường dẫn, cắt 255 ký tự, rỗng → `tai-lieu.pdf`.
4. Giới hạn hiệu lực = `MAX_FILE_SIZE_MB` nếu có, ngược lại `HARD_MAX_UPLOAD_MB`.

## Tiêu chí hoàn thành

- [ ] Test (gắn `req`): tệp đúng giới hạn được nhận, vượt 1 byte bị từ chối `FILE_TOO_LARGE` kèm giới hạn (US-001-AC2); `.docx` hoặc `.pdf` giả (nội dung `MZ…`) bị `UNSUPPORTED_TYPE` (US-001-AC3).
- [ ] Test: tên `../../etc/passwd.pdf` → không còn `/` hay `..`; SHA-256 khớp `hashlib` trên toàn bộ nội dung.
- [ ] Test: luồng 1 GB giả lập (generator) bị dừng sau khi vượt giới hạn mà không đọc hết (đo số byte đã đọc).
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Chưa lưu vào kho hay CSDL (S1-02).
- Chưa có endpoint (S1-03).

## Ghi chú và rủi ro

- Số `[TBD: OQ-009]` luôn đến từ cấu hình; không viết giá trị cứng trong mã.
