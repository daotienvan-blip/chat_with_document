# S2-04 — IngestionService.process: từ PDF đến đoạn có vector và trạng thái ready/failed

| | |
|---|---|
| **Lát cắt** | S2 — Xử lý tài liệu đến khi sẵn sàng hoặc lỗi (UC09, UC10) (mốc M1) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S2-01](S2-01-pdfextractor-pymupdf-chay-trong-tien-trinh.md), [S2-02](S2-02-chunker-chia-doan-600-token-chong-100-giu.md), [S2-03](S2-03-hang-doi-viec-nen-claim-complete-fail-sweep.md), [S1-02](S1-02-documentrepository-jobrepository-enqueue-va.md) |
| **Truy vết** | UC09, UC10, US-002-AC1, US-003-AC1, US-003-AC2, US-003-AC3, BR-002, BR-018, QAS-03 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Chunker, hàng đợi (đồng thời, backoff, hoàn lần thử), xử lý tài liệu (idempotent, xóa giữa chừng) |

## Mục tiêu

Xử lý một tài liệu theo đúng luồng Blueprint §3.6.1, idempotent, an toàn khi bị xóa giữa chừng.

## Đọc trước

- Blueprint §3.6.1, §3.7.1
- Database_Design §5.1 (T3)
- SAD §3.2.1
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/cwd_server/core/ingestion/service.py`
- `server/cwd_server/persistence/repositories.py` (ChunkRepository.add_batch, DocumentRepository.set_ready/set_failed, lock_for_update)
- `server/tests/integration/test_ingestion_service.py`

## Các bước

1. Luồng: lấy tài liệu (đã xóa mềm hoặc không còn → kết thúc êm) → `ObjectStorePort.get` → `extract` → nếu mọi trang rỗng ⇒ `NO_EXTRACTABLE_TEXT` → `Chunker` → `LlmPort.embed` theo lô 64 → **một giao dịch**: `SELECT … FOR UPDATE` tài liệu, nếu `deleted_at` khác null thì rollback; ngược lại chèn đoạn `ON CONFLICT DO NOTHING` và `set_ready(page_count)`.
2. Ánh xạ lỗi: `PdfCorrupt`→`FILE_CORRUPT`, `PdfEncrypted`→`FILE_ENCRYPTED`, 0 đoạn→`NO_EXTRACTABLE_TEXT` (đều kết thúc, không thử lại); `AiUnavailable/AiTimeout/PdfTimeout`/lỗi kho → ném lỗi thử lại được cho `Runner`; hết số lần thử → `set_failed(PROCESSING_ERROR)`.
3. Kiểm tra số chiều vector bằng `EMBEDDING_DIM`; sai → lỗi cấu hình rõ ràng (không ghi dữ liệu).
4. Đăng ký handler `process_document` cho `Runner`.

## Tiêu chí hoàn thành

- [ ] `make test-int` xanh: thành công (có đoạn, `ready`, `page_count` đúng); hỏng / có mật khẩu / ảnh quét → đúng `failure_reason`; chạy lại hai lần không tạo đoạn trùng; tài liệu bị xóa mềm trước khi commit → 0 đoạn được ghi.
- [ ] Test AI lỗi tạm thời: lần 1 lỗi, lần 2 thành công → `ready`; 3 lần lỗi → `failed/PROCESSING_ERROR`.
- [ ] Test gắn `req`: US-002-AC1, US-003-AC1/AC2/AC3.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Entry point worker (S2-05).
- Handler `purge_document` (S6-02).

## Ghi chú và rủi ro

- Một tài liệu `ready` mà 0 đoạn là trạng thái cấm (Database_Design §3.4.5).
