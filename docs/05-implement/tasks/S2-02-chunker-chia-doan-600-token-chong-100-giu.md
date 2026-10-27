# S2-02 — Chunker: chia đoạn ~600 token, chồng 100, giữ biên trang

| | |
|---|---|
| **Lát cắt** | S2 — Xử lý tài liệu đến khi sẵn sàng hoặc lỗi (UC09, UC10) (mốc M1) |
| **Cỡ** | S (1–3 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S0-05](S0-05-kieu-mien-cong-ports-adapter-gia-va.md) |
| **Truy vết** | UC09, BR-008 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Chunker, hàng đợi (đồng thời, backoff, hoàn lần thử), xử lý tài liệu (idempotent, xóa giữa chừng) |

## Mục tiêu

Hàm thuần biến danh sách trang thành các `ChunkDraft` có `page_start/page_end` đúng.

## Đọc trước

- Blueprint §3.2.3, §3.4.4
- SAD §3.1 (tham số RAG)
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/cwd_server/core/ingestion/chunker.py`
- `server/tests/unit/test_chunker.py`

## Các bước

1. `Chunker(chunk_tokens, overlap, counter)`; `TokenCounter` mặc định đếm từ (tách khoảng trắng) `[Đề xuất]`, thay được khi chốt mô hình (OQ-S01).
2. `split(pages) -> list[ChunkDraft(chunk_index, page_start, page_end, text)]`: chỉ số liên tục từ 0; đoạn qua ranh giới trang giữ cả hai số trang; trang rỗng bị bỏ qua; một trang rất dài bị tách; có trần độ dài ký tự cứng để bảo vệ `tsvector`.
3. Tính xác định: cùng đầu vào → cùng đầu ra.

## Tiêu chí hoàn thành

- [ ] Test thuộc tính: `chunk_index` liên tục, `page_start ≤ page_end`, không đoạn rỗng, mọi từ của trang xuất hiện ít nhất một lần.
- [ ] Test: chồng lấp đúng ~100 từ giữa hai đoạn kề nhau; đoạn qua trang 3–4 có `page_start=3, page_end=4`.
- [ ] Test: toàn trang rỗng → danh sách rỗng.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Gọi embedding (S2-04).

## Ghi chú và rủi ro

- Kích thước và chồng lấp lấy từ cấu hình `rag.chunk_*`.
