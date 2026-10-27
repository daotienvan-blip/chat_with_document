# S4-01 — Kiểm thử đầu-cuối số trang đúng và gộp trang nguồn

| | |
|---|---|
| **Lát cắt** | S4 — Số trang và mở tài liệu nguồn (UC16, UC17) (mốc M2) |
| **Cỡ** | S (1–3 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S3-03](S3-03-answerservice-g-l1-goi-llm-g-l2-dung-nguon.md), [S2-04](S2-04-ingestionservice-process-tu-pdf-den-doan-co.md) |
| **Truy vết** | UC16, US-008-AC1, AC-008 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Trang đúng; lưu ý: trang = phạm vi trang của đoạn (đoạn ~600 từ có thể trải 2 trang) |

## Mục tiêu

Chứng minh số trang trong nguồn khớp trang thật của nội dung, kể cả khi đoạn nằm vắt qua hai trang.

## Đọc trước

- Blueprint §3.2.1 (SourceRef)
- BRD AC-008
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/tests/integration/test_source_pages.py`
- sửa lỗi phát hiện được ở `chunker.py`/`answer/service.py` nếu có

## Các bước

1. Sinh PDF 6 trang, mỗi trang chứa token duy nhất (`ZXQ1…ZXQ6`) và một đoạn dài vắt qua trang 3–4; tải qua pipeline thật (extractor + chunker + `FakeLlm` + PostgreSQL).
2. Hỏi theo từng token với `FakeLlm` kịch bản trích đoạn chứa token: khẳng định `sources[0].pages` đúng trang (một số); với đoạn vắt trang khẳng định `[3,4]`.
3. Khẳng định `pages` luôn tăng dần, không trùng, bắt đầu từ 1.

## Tiêu chí hoàn thành

- [ ] `make test-int` xanh; test gắn `req` US-008-AC1.
- [ ] Mọi lỗi lệch trang tìm được đã được sửa kèm test hồi quy.
- [ ] Báo cáo ngắn trong PR: số trường hợp kiểm tra và kết quả.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Giao diện (S4-03).

## Ghi chú và rủi ro

- Đây là kiểm tra AC-008 “mẫu kiểm tra”; bộ mẫu thật do business owner cung cấp (DEP-002).
