# S3-04 — Adapter LlmPort qua HTTP (tương thích OpenAI) với cấu hình nhà cung cấp

| | |
|---|---|
| **Lát cắt** | S3 — Hỏi đáp có nguồn: có căn cứ hoặc không tìm thấy (UC14, UC15, UC19, UC21) (mốc M2) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S0-05](S0-05-kieu-mien-cong-ports-adapter-gia-va.md) |
| **Truy vết** | UC21, C-08 |
| **Bị chặn bởi** | OQ-005, OQ-S01 (chỉ chặn việc dùng cho dữ liệu thật, không chặn mã) |
| **Trạng thái** | 🟡 Một phần (2026-10-27) — Adapter HTTP kiểm bằng MockTransport; **chưa gọi nhà cung cấp thật** (chặn OQ-005, OQ-S01) |

## Mục tiêu

Một adapter thật cho `embed` và `generate` có thể trỏ tới nhà cung cấp hoặc máy chủ tự lưu trữ có API tương thích OpenAI, đọc cấu hình từ môi trường.

## Đọc trước

- Blueprint §3.2.2, §3.5.3
- SAD ADR-05
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/cwd_server/adapters/llm_http.py`
- `server/tests/unit/test_llm_http.py` (httpx MockTransport)

## Các bước

1. Cấu hình: `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_EMBED_MODEL`, `LLM_CHAT_MODEL`, `EMBEDDING_DIM`.
2. `embed(texts)`: gọi theo lô; kiểm tra số chiều trả về bằng `EMBEDDING_DIM`, sai ⇒ lỗi cấu hình rõ ràng.
3. `generate(system, user, schema)`: nhiệt độ 0, yêu cầu đầu ra JSON theo schema; trả `dict`.
4. Lỗi: hết thời gian ⇒ `AiTimeout`; 5xx/kết nối/429 ⇒ `AiUnavailable`; 4xx khác ⇒ lỗi cấu hình. **Không bao giờ** ghi thân yêu cầu/phản hồi hay khóa API vào log.

## Tiêu chí hoàn thành

- [ ] `make check` xanh; test với `MockTransport` cho từng nhánh lỗi, kiểm tra số chiều, và header `Authorization` không xuất hiện trong log.
- [ ] Có bước thử tay tùy chọn (`make llm-smoke`) chạy với khóa thật nếu có, bỏ qua khi không có biến môi trường.
- [ ] Không import SDK nhà cung cấp trong `core/` (import-linter xanh).
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Timeout/retry/breaker (S7-02).
- Chọn nhà cung cấp chính thức.

## Ghi chú và rủi ro

- Chọn giao thức “tương thích OpenAI” là `[Đề xuất]` vì hầu hết nhà cung cấp và máy chủ tự lưu trữ hỗ trợ; nhà cung cấp thật chờ OQ-005 và OQ-S01.
