# S8-04 — Bộ đánh giá chất lượng AI (eval): tập câu hỏi, chỉ số, báo cáo lặp lại được

| | |
|---|---|
| **Lát cắt** | S8 — Củng cố, vận hành và cổng phát hành (mốc M4) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S3-05](S3-05-api-post-questions.md), [S3-04](S3-04-adapter-llmport-qua-http-tuong-thich-openai.md) |
| **Truy vết** | MET-002, BR-011, G3, G4, G5, US-006-AC3, DEP-002 |
| **Bị chặn bởi** | OQ-004, DEP-002 (cho bộ dữ liệu thật) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Công cụ + bộ tổng hợp + CSV cho người chấm. G3 chặn OQ-004/DEP-002 |

## Mục tiêu

Chạy lặp lại bộ câu hỏi chuẩn để tính tỷ lệ nguồn hợp lệ, `not_found` đúng và xuất bảng chấm điểm cho người xác nhận.

## Đọc trước

- BRD MET-002, DEP-002
- PRD §5.1 (G3–G5)
- Blueprint §3.1.1 (eval)
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `eval/{dataset.py,run.py,metrics.py,report.py,fixtures.py}`
- `eval/datasets/synthetic.jsonl` + sinh PDF tổng hợp
- `make eval`

## Các bước

1. Định dạng JSONL: `{id, question, kind: in_scope|out_of_scope|multi_doc, expected_status, expected_docs, expected_pages?, reference_answer?}`.
2. Bộ tổng hợp (PDF sinh bằng mã) để chạy trong CI với `FakeLlm`; bộ thật của business owner (DEP-002) đặt ở nơi khác, không commit nội dung nhạy cảm.
3. Chỉ số tự động: tỷ lệ nguồn có tài liệu/trang đúng (G4), tỷ lệ câu hỏi ngoài tài liệu nhận `not_found` (G5), tỷ lệ trích dẫn hợp lệ, độ ổn định giữa các lần chạy. Độ đúng của nội dung (G3, MET-002) cần người chấm: xuất CSV (câu hỏi, câu trả lời, nguồn, cột chấm) để người xác nhận điền.
4. Adapter ghi-phát (record/replay) để chạy lại có kết quả giống hệt; báo cáo Markdown có phiên bản mô hình/cấu hình.

## Tiêu chí hoàn thành

- [ ] `make eval` chạy với `FakeLlm` và bộ tổng hợp, ra báo cáo và CSV; chạy hai lần cho cùng kết quả.
- [ ] Chạy được với `LLM_PROVIDER=http` khi có khóa (không bắt buộc cho tiêu chí hoàn thành).
- [ ] Ngưỡng đạt/không đạt đọc từ cấu hình; **không** có số mặc định cho ngưỡng độ đúng `[TBD: OQ-004]`.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Chọn ngưỡng; tạo bộ câu hỏi thật.

## Ghi chú và rủi ro

- Phụ thuộc DEP-002 để có ý nghĩa nghiệp vụ; task này chỉ dựng công cụ.
