# S7-02 — Chịu lỗi cho LlmPort: timeout, retry có lùi, circuit breaker

| | |
|---|---|
| **Lát cắt** | S7 — Chịu lỗi và quá tải (mốc M4) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S3-04](S3-04-adapter-llmport-qua-http-tuong-thich-openai.md), [S2-04](S2-04-ingestionservice-process-tu-pdf-den-doan-co.md) |
| **Truy vết** | QAS-03, C-11, EC-15 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — LoadGuard + rate limit; retry + breaker; lỗi UI + đếm ngược; đối soát |

## Mục tiêu

Dịch vụ AI chậm hoặc ngưng không làm treo API hay đốt hết số lần thử của worker.

## Đọc trước

- SAD §4.2
- Blueprint §3.7.5, §3.8.2, §3.6.1 (count_attempt)
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `adapters/resilient_llm.py` (bọc `LlmPort`)
- `worker/runner.py` (nhận biết breaker mở)
- `server/tests/unit/test_resilient_llm.py`

## Các bước

1. Hết thời gian: `embed` 10 s, `generate` 30 s, tổng yêu cầu hỏi đáp 40 s (hạn chót truyền xuống).
2. Retry có lùi lũy thừa + nhiễu (tenacity): `embed` 2 lần, `generate` 1 lần; chỉ với lỗi tạm thời, không với 4xx.
3. Circuit breaker: 5 lỗi liên tiếp ⇒ mở 30 s ⇒ nửa mở (một lần thử) ⇒ đóng khi thành công; khi mở ném `AiUnavailable` ngay (< 1 s).
4. Worker: lỗi do breaker mở ⇒ `fail(..., count_attempt=false)` và `run_after` dời tới lúc nửa mở.

## Tiêu chí hoàn thành

- [ ] `make check` xanh với `FakeLlm` gây lỗi và đồng hồ giả: đúng số lần thử, đúng độ lùi, breaker chuyển trạng thái đúng chuỗi.
- [ ] Test: khi breaker mở, `POST /questions` trả `502 AI_UNAVAILABLE` rất nhanh và `GET /documents`, `DELETE` vẫn hoạt động.
- [ ] Test (QAS-03): IF-02 ngưng rồi hồi phục ⇒ tài liệu đang xử lý cuối cùng `ready`, không mất lần thử.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Hiển thị lỗi (S7-03).
