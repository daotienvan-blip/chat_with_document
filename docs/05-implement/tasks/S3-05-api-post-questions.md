# S3-05 — API POST /questions

| | |
|---|---|
| **Lát cắt** | S3 — Hỏi đáp có nguồn: có căn cứ hoặc không tìm thấy (UC14, UC15, UC19, UC21) (mốc M2) |
| **Cỡ** | S (1–3 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S3-03](S3-03-answerservice-g-l1-goi-llm-g-l2-dung-nguon.md), [S0-03](S0-03-nen-tang-server-cau-hinh-log-loi-problem.md) |
| **Truy vết** | UC14, US-006-AC1, US-010-AC1, BR-006 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — xem IMPLEMENTATION_STATUS.md |

## Mục tiêu

Endpoint hỏi đáp đúng hợp đồng, kể cả kiểm tra đầu vào và ánh xạ lỗi AI.

## Đọc trước

- openapi.yaml (askQuestion)
- API_Design §3.5.2 mục 7
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/cwd_server/api/routers/questions.py`
- `server/tests/api/test_questions_api.py`

## Các bước

1. Kiểm tra: sau `trim` rỗng ⇒ `400 EMPTY_QUESTION`; dài hơn `MAX_QUESTION_LENGTH` (nếu có) ⇒ `400 QUESTION_TOO_LONG` kèm `limit`; thân sai hình dạng/trường thừa ⇒ `INVALID_REQUEST`.
2. Gọi `AnswerService.ask`; `AiUnavailable` ⇒ `502`, `AiTimeout` ⇒ `504`; `Cache-Control: no-store`.
3. Kiểm thử bất biến `Answer` với `assert_matches_openapi` và các khẳng định thêm: `not_found` ⇒ `sources=[]`; `answered/partial` ⇒ `sources≥1`.
4. Xác nhận không ghi nội dung câu hỏi vào log (bắt log trong test).

## Tiêu chí hoàn thành

- [ ] `make check` xanh.
- [ ] Test: ba trạng thái hợp lệ trả `200`; lỗi đúng mã; log không chứa câu hỏi mẫu.
- [ ] Gọi tay: `curl -X POST …/api/v1/questions` với dữ liệu gieo sẵn trả `answered` có nguồn.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- LoadGuard và giới hạn tốc độ (S7-01).

## Ghi chú và rủi ro

- Mốc M2 (backend) đạt khi S3-05 và S4-02 xong.
