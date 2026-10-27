# S6-02 — Handler purge_document và cuộc đua xử lý ↔ xóa

| | |
|---|---|
| **Lát cắt** | S6 — Xóa tài liệu (UC12) (mốc M3) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S6-01](S6-01-xoa-mem-documentservice-delete-api-delete.md), [S2-05](S2-05-worker-entrypoint-vong-quet-tat-em-va-kiem.md) |
| **Truy vết** | UC12, US-005-AC2, D-01, DQ-02 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Xóa mềm, purge đúng thứ tự, race, hộp thoại tiếp cận |

## Mục tiêu

Xóa vật lý đúng thứ tự (tệp trước, bản ghi sau), idempotent, và không bao giờ có tài liệu vừa xóa vừa `ready` vẫn truy xuất được.

## Đọc trước

- Database_Design §3.4.4 (thứ tự xóa), §5.1 (cuộc đua T3↔T4)
- Blueprint §3.6.3
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `worker/handlers/purge.py`
- đăng ký handler trong `worker/__main__.py`
- `server/tests/integration/test_purge_and_races.py`

## Các bước

1. Handler: `ObjectStorePort.delete(storage_key)` (idempotent) ⇒ `DELETE FROM documents WHERE id=:id` (cascade `chunks`) ⇒ `complete(job)`; chỉ chạy khi `deleted_at IS NOT NULL`; lỗi ở bước nào thì thử lại được.
2. Kiểm thử cuộc đua bằng hai kết nối: (a) `DELETE` đến trước khi worker finalize ⇒ worker thấy `deleted_at` và không ghi đoạn; (b) worker finalize xong rồi `DELETE` ⇒ tài liệu `ready` rồi bị loại khỏi truy xuất ngay.
3. Việc `process_document` còn trong hàng đợi cho tài liệu đã purge ⇒ kết thúc êm (không lỗi).
4. Đối chiếu: sau purge, 0 dòng `documents/chunks` và 0 đối tượng trong kho.

## Tiêu chí hoàn thành

- [ ] `make test-int` xanh gồm cả hai kịch bản đua và purge hai lần.
- [ ] Chạy thử với `PURGE_DELAY=1s`: sau ≥ 1 s tài liệu biến mất hoàn toàn khỏi CSDL và kho.
- [ ] Test chèn lỗi giữa bước xóa tệp và xóa bản ghi ⇒ thử lại hoàn tất, không để tệp mồ côi.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Đối soát định kỳ (S7-04).
