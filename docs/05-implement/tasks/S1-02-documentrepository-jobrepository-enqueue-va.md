# S1-02 — DocumentRepository, JobRepository.enqueue và DocumentService.upload nguyên tử

| | |
|---|---|
| **Lát cắt** | S1 — Tải PDF lên và xem danh sách (UC07, UC08, UC11) (mốc M1) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S0-04](S0-04-csdl-migration-0001-phien-lam-viec-va-kiem.md), [S0-06](S0-06-adapter-object-storage-s3-va-quy-tac-phu.md), [S1-01](S1-01-kiem-tra-tep-tai-len-uc08-kich-thuoc-duoi.md) |
| **Truy vết** | UC07, US-001-AC1, US-003-AC4, BR-001 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Kiểm tra tệp, tải lên nguyên tử + bù trừ, API, danh sách + polling, tải lên có tiến độ/hủy/thử lại |

## Mục tiêu

Tải lên lưu tệp vào kho rồi tạo bản ghi `processing` + việc nền trong **một** giao dịch; lỗi ở bất kỳ bước nào không để lại tài liệu nửa vời.

## Đọc trước

- Blueprint §3.4.3, §3.6.1
- API_Design §3.5.2 mục 2 (thứ tự ghi)
- Database_Design §5.1 (T1)
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/cwd_server/persistence/repositories.py` (Document, Job)
- `server/cwd_server/core/documents/service.py` (`upload`, `list`, `get`)
- `server/tests/integration/test_upload_service.py`

## Các bước

1. `DocumentRepository`: `add`, `get_visible(id)`, `list_visible()` (sắp `created_at` giảm dần, lọc `deleted_at IS NULL`). `JobRepository.enqueue(job)` dùng `INSERT … ON CONFLICT DO NOTHING`.
2. `DocumentService.upload`: `storage_key = documents/{uuid}.pdf` → `ObjectStorePort.put` → giao dịch `INSERT documents(processing)` + `INSERT jobs(process_document, request_id)` → trả `Document`.
3. Bù trừ: nếu giao dịch lỗi thì `ObjectStorePort.delete` đối tượng vừa ghi rồi ném lỗi; nếu `put` lỗi thì không chạm CSDL (`StorageUnavailable`).
4. Test chèn lỗi ở từng bước (kho lỗi, CSDL lỗi, kết nối ngắt giữa chừng) và kiểm tra: 0 dòng `documents`, 0 `jobs`, 0 đối tượng mồ côi.

## Tiêu chí hoàn thành

- [ ] `make test-int` xanh; test gắn `req` US-001-AC1 (tải thành công tạo `processing` và đối tượng trong kho) và US-003-AC4 (lỗi giữa chừng → không có tài liệu nửa vời).
- [ ] Test: hai lần tải cùng nội dung tạo hai tài liệu (chưa chặn trùng, OQ-014).
- [ ] Test: liệt kê không bao giờ trả tài liệu `deleted_at` khác null (tạo trực tiếp bằng SQL).
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Chưa có API (S1-03) hay worker (S2-*).
- Xóa (S6-01).

## Ghi chú và rủi ro

- Đối soát đối tượng mồ côi sau sập tiến trình thuộc S7-04.
