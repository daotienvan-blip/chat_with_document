# S5-01 — Backend: tổng hợp nhiều tài liệu, mâu thuẫn và trả lời một phần

| | |
|---|---|
| **Lát cắt** | S5 — Tổng hợp nhiều tài liệu và trả lời một phần (UC18, UC19) (mốc M3) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S3-03](S3-03-answerservice-g-l1-goi-llm-g-l2-dung-nguon.md) |
| **Truy vết** | UC18, UC19, US-009-AC1, US-009-AC2, US-010-AC2, US-007-AC2, BR-009, AC-009 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — OQ-A03 (trường `missing`) chưa quyết định ⇒ không đổi hợp đồng |

## Mục tiêu

Câu hỏi cần ≥ 2 tài liệu cho một câu trả lời nêu đủ các nguồn; mâu thuẫn và phần thiếu được nêu rõ; không bao giờ có `partial` thiếu nguồn.

## Đọc trước

- Blueprint §3.4.4 (max_chunks_per_doc), §3.5.3 (quy tắc 3–4)
- API_Design §3.5.2 mục 7
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `core/answer/prompt.py` (tinh chỉnh), `core/answer/service.py`
- `server/tests/integration/test_multi_doc_answers.py`

## Các bước

1. Gieo hai tài liệu mỗi cái chứa một nửa thông tin; xác nhận Retrieval đưa đoạn của **cả hai** vào lời nhắc (giới hạn 4/tài liệu), và `sources` liệt kê đủ hai tài liệu (US-009-AC1).
2. Kịch bản mâu thuẫn: hai tài liệu nêu giá trị khác nhau ⇒ lời nhắc yêu cầu nêu khác biệt và dẫn từng đoạn; kiểm tra ở mức cấu trúc (có trích dẫn cả hai) bằng `FakeLlm` kịch bản (US-009-AC2).
3. `partial`: giữ bất biến `sources ≥ 1`; nếu LLM trả `partial` nhưng không còn trích dẫn hợp lệ thì hạ về `not_found` (G-L2). Sắp xếp `sources` theo độ liên quan cao nhất của tài liệu.
4. Quyết định thiết kế cần ghi lại: có thêm trường tùy chọn `missing` vào `Answer` để giao diện tách khối “Không tìm thấy” hay không (PLAN §8, **OQ-A03**). Mặc định: **không** đổi hợp đồng; `answer` chứa cả hai phần.

## Tiêu chí hoàn thành

- [ ] `make test-int` xanh; test gắn `req` US-009-AC1, US-009-AC2, US-010-AC2, US-007-AC2.
- [ ] Test: không tài liệu thừa trong `sources` khi câu trả lời chỉ dùng một tài liệu.
- [ ] Nếu OQ-A03 được chấp thuận trước khi làm: cập nhật `openapi.yaml`, `API_Design.md`, kiểu web đã sinh (thay đổi cộng thêm).
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Hiển thị giao diện (S5-02).
- Chất lượng thật trên mô hình thật (S8-04).

## Ghi chú và rủi ro

- Lời nhắc thật chỉ kiểm chứng được cấu trúc bằng `FakeLlm`; chất lượng ngữ nghĩa cần S8-04.
