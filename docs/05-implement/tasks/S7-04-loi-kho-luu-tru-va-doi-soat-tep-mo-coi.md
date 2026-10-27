# S7-04 — Lỗi kho lưu trữ và đối soát tệp mồ côi

| | |
|---|---|
| **Lát cắt** | S7 — Chịu lỗi và quá tải (mốc M4) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S2-05](S2-05-worker-entrypoint-vong-quet-tat-em-va-kiem.md), [S6-02](S6-02-handler-purge-document-va-cuoc-dua-xu-ly-xoa.md) |
| **Truy vết** | US-003-AC4, D-05, Database_Design §5.4 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — LoadGuard + rate limit; retry + breaker; lỗi UI + đếm ngược; đối soát |

## Mục tiêu

Kho lưu trữ lỗi được báo đúng; đối soát định kỳ dọn tệp mồ côi và sửa tài liệu không nhất quán.

## Đọc trước

- Database_Design §5.4
- SAD §4.2
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `worker/reconcile.py`
- ánh xạ lỗi kho trong `api/`
- `server/tests/integration/test_reconcile.py`

## Các bước

1. `StorageUnavailable` ⇒ `503 STORAGE_UNAVAILABLE` ở `POST /documents` và `GET …/file` (kèm `Retry-After`).
2. `reconcile()` (mỗi giờ `[Đề xuất]`): đối tượng `documents/*` không có dòng `documents` và cũ hơn 24 giờ ⇒ xóa; dòng `documents` không còn đối tượng ⇒ `failed/PROCESSING_ERROR` + cảnh báo; `ready` nhưng 0 đoạn ⇒ xếp lại `process_document`.
3. Test mô phỏng sập giữa `put` và giao dịch ⇒ lần quét sau dọn đối tượng; tệp mới (< 24 giờ) không bị xóa nhầm.

## Tiêu chí hoàn thành

- [ ] `make test-int` xanh cho ba kịch bản đối soát và hai mã `503`.
- [ ] Test: `reconcile()` chạy hai lần liên tiếp không đổi gì thêm (idempotent).
- [ ] Cảnh báo ghi qua log có cấu trúc, không chứa nội dung tài liệu.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Sao lưu/khôi phục (S8-07).
