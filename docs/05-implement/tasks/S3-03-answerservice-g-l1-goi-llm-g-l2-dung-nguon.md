# S3-03 — AnswerService: G-L1, gọi LLM, G-L2, dựng nguồn từ siêu dữ liệu (G-L3)

| | |
|---|---|
| **Lát cắt** | S3 — Hỏi đáp có nguồn: có căn cứ hoặc không tìm thấy (UC14, UC15, UC19, UC21) (mốc M2) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S3-01](S3-01-chunkrepository-retrievalservice-vector-tu.md), [S3-02](S3-02-loi-nhac-schema-dau-ra-llm-va.md) |
| **Truy vết** | UC14, UC15, UC19, UC21, US-006-AC1, US-007-AC1, US-007-AC2, US-010-AC1, BR-006, BR-007, BR-010, QAS-10 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Truy xuất lai + RRF + giới hạn/tài liệu; lời nhắc + G-L2; AnswerService G-L1/G-L2/G-L3, test race xóa |

## Mục tiêu

`ask(question) -> AnswerResult` thực hiện đủ ba lớp bảo vệ; nguồn lấy từ cơ sở dữ liệu, không từ văn bản LLM.

## Đọc trước

- SAD §2.2.4
- Blueprint §3.6.2
- API_Design §3.5.2 mục 7 (bất biến Answer)
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/cwd_server/core/answer/service.py`
- `server/cwd_server/core/answer/messages.py` (`NOT_FOUND_MESSAGE`)
- `server/tests/integration/test_answer_service.py`

## Các bước

1. Luồng: `retrieve` → **G-L1** (rỗng hoặc điểm vector cao nhất < `rag.min_relevance` ⇒ `not_found`, **không gọi LLM**) → `generate` (`AiBadOutput`: thử lại 1 lần, vẫn sai ⇒ `not_found`) → **G-L2** `validate` → `ChunkRepository.by_ids(mã hợp lệ)` (lọc searchable) → **G-L3** dựng `SourceRef` theo tài liệu với `pages` gộp, tăng dần, không trùng (gộp mọi trang từ `page_start..page_end`).
2. Nếu `by_ids` không còn đoạn nào (tài liệu vừa bị xóa) ⇒ `not_found`.
3. `not_found` luôn dùng hằng `NOT_FOUND_MESSAGE` (“Không tìm thấy thông tin trong các tài liệu đã tải.”), `sources=[]`.
4. Mặc định `rag.min_relevance` cho phát triển là 0 (chỉ chặn khi rỗng); giá trị thật `[TBD: hiệu chỉnh bằng DEP-002/OQ-004]` — **không** bịa số.

## Tiêu chí hoàn thành

- [ ] `make test-int` xanh với `FakeLlm` kịch bản: câu hỏi có trong tài liệu → `answered` + nguồn đúng tên; ngoài tài liệu → `not_found` và `generate` **không được gọi** (đếm lần gọi); LLM trả mã bịa → loại; LLM đặt tên nguồn trong `answer` không ảnh hưởng `sources`.
- [ ] Test gắn `req`: US-006-AC1, US-007-AC1, US-007-AC2 (đúng N tài liệu, không thừa), US-010-AC1.
- [ ] Test race: xóa mềm tài liệu giữa `retrieve` và `by_ids` ⇒ nguồn của nó không xuất hiện.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Endpoint (S3-05)
- Trả lời nhiều tài liệu và `partial` được tinh chỉnh ở S5-01.

## Ghi chú và rủi ro

- Đây là task cốt lõi của chất lượng; đọc kỹ SAD §2.2.4 trước khi sửa.
