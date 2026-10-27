# S3-01 — ChunkRepository + RetrievalService: vector, từ khóa, RRF, giới hạn mỗi tài liệu

| | |
|---|---|
| **Lát cắt** | S3 — Hỏi đáp có nguồn: có căn cứ hoặc không tìm thấy (UC14, UC15, UC19, UC21) (mốc M2) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S2-04](S2-04-ingestionservice-process-tu-pdf-den-doan-co.md), [S3-00](S3-00-spike-hnsw-so-voi-quet-chinh-xac-khi-co.md) |
| **Truy vết** | UC21, US-002-AC2, BR-006, BR-009, D-01 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Truy xuất lai + RRF + giới hạn/tài liệu; lời nhắc + G-L2; AnswerService G-L1/G-L2/G-L3, test race xóa |

## Mục tiêu

Truy xuất lai trả tối đa 8 đoạn, tối đa 4 đoạn mỗi tài liệu, **chỉ** từ tài liệu `ready` và chưa xóa.

## Đọc trước

- Blueprint §3.4.3, §3.4.4, §3.6.2
- Database_Design §3.4.2 (Q3–Q5)
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/cwd_server/persistence/repositories.py` (mở rộng `ChunkRepository` đã có `add_batch` từ S2-04)
- `server/cwd_server/core/retrieval/{service,tsquery,rrf}.py`
- `server/tests/{unit,integration}/test_retrieval*.py`

## Các bước

1. `vector_candidates`, `fts_candidates`, `by_ids` — mọi truy vấn có điều kiện searchable (`status='ready' AND deleted_at IS NULL`), tham số liên kết, theo chế độ `RETRIEVAL_MODE` từ S3-00.
2. `build_tsquery(question)`: tách từ chữ/số Unicode, hạ chữ thường, tối đa 12 từ, nối bằng `|`; câu hỏi không còn từ nào → bỏ nhánh FTS. Không ghép chuỗi SQL.
3. RRF (k=60) trong ứng dụng; chọn 8 đoạn với tối đa 4 mỗi tài liệu; trả kèm điểm vector cao nhất (cho G-L1).
4. Test tích hợp với `FakeLlm` và đoạn gieo trực tiếp: đoạn của tài liệu `processing`, `failed`, đã xóa mềm **không bao giờ** xuất hiện (US-002-AC2); giới hạn 4/tài liệu; câu hỏi chứa ký tự đặc biệt (`'`, `&`, `|`, `:`) không gây lỗi.

## Tiêu chí hoàn thành

- [ ] `make test-int` xanh; test gắn `req` US-002-AC2.
- [ ] Unit: RRF cho thứ hạng đúng trên ví dụ nhỏ tính tay; `build_tsquery` không bao giờ sinh chuỗi gây lỗi cú pháp (kiểm bằng fuzz đơn giản).
- [ ] Tham số lấy từ cấu hình `rag.*`, không hằng số trong mã.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Gọi LLM sinh câu trả lời (S3-03).

## Ghi chú và rủi ro

- Ngưỡng liên quan `rag.min_relevance` do S3-03 áp dụng.
