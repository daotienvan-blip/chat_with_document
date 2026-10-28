# Release notes — v0.1.0 (MVP) — BẢN NHÁP

> Trạng thái: **chưa phát hành** (`release-record.md` §0). Dành cho người dùng thí điểm và CNTT.

## Có gì

Ứng dụng web để tải PDF lên, đặt câu hỏi và nhận câu trả lời kèm nguồn (tên tài liệu, số trang). Khi tài liệu không có thông tin, ứng dụng trả lời "không tìm thấy".

| Nhóm | Chức năng (use case) |
|---|---|
| Tài liệu | Tải PDF lên, có tiến độ, hủy và thử lại (UC07–UC10) · Xem danh sách và trạng thái xử lý (UC11) · Xóa tài liệu (UC12) |
| Hỏi đáp | Đặt câu hỏi trên mọi tài liệu đã sẵn sàng (UC14) · Xem nguồn, mở đúng trang PDF (UC15–UC17) · Báo "không tìm thấy" (UC18) · Báo lỗi khi dịch vụ AI không sẵn sàng (UC19) |

Hướng dẫn: `guide/HUONG_DAN_SU_DUNG.md`.

## Giới hạn đã biết

| Mã | Giới hạn | Ảnh hưởng người dùng |
|---|---|---|
| DEF-001 | Câu hỏi ngoài tài liệu đôi khi vẫn được trả lời bằng các câu không liên quan | **Luôn mở nguồn để kiểm** trước khi dùng thông tin |
| — | Không đăng nhập; mọi người trong mạng được phép dùng chung một kho tài liệu (CON-005) | Không tải tài liệu mà không phải ai trong nhóm cũng được đọc |
| — | Bản phát hành đầu dùng AI trích xuất cục bộ: câu trả lời là câu trích nguyên văn, không diễn giải | Câu trả lời có thể cụt; mở nguồn để đọc ngữ cảnh |
| — | PDF dạng ảnh quét (không có lớp chữ) không đọc được | Tài liệu báo lỗi "không có nội dung chữ" |
| OQ-D01 | Tài liệu đã xóa còn trong bản sao lưu tới 7 ngày | Báo CNTT nếu cần xóa khẩn cấp |
| — | Chưa kiểm trên trình duyệt tự động; giao diện thử tay trên Chrome/Safari macOS | Báo lỗi hiển thị cho nhóm dự án |

## Cho CNTT

- Thành phần: 2 bản api (FastAPI), 1 worker, nginx (TLS ≥ 1.2, allowlist), PostgreSQL 17 + pgvector, kho S3-compatible.
- Công tắc cấu hình: `release-record.md` §4. Rollback: `rollback-plan.md`. Vận hành: `docs/10-operations/`.
- Thay đổi so với thiết kế: `docs/05-implement/IMPLEMENTATION_STATUS.md`.
