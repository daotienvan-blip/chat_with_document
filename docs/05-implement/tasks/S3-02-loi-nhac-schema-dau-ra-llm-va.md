# S3-02 — Lời nhắc, schema đầu ra LLM và GroundingValidator

| | |
|---|---|
| **Lát cắt** | S3 — Hỏi đáp có nguồn: có căn cứ hoặc không tìm thấy (UC14, UC15, UC19, UC21) (mốc M2) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S0-05](S0-05-kieu-mien-cong-ports-adapter-gia-va.md) |
| **Truy vết** | UC15, UC19, US-006-AC3, US-007-AC1, US-010-AC1, QAS-10, BRU-001 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Truy xuất lai + RRF + giới hạn/tài liệu; lời nhắc + G-L2; AnswerService G-L1/G-L2/G-L3, test race xóa |

## Mục tiêu

Phần thuần (không I/O) dựng lời nhắc, phân tích đầu ra LLM và loại mọi trích dẫn không hợp lệ.

## Đọc trước

- Blueprint §3.5.3
- SAD §2.2.4 (G-L2, G-L3)
- BRD BRU-001/002
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/cwd_server/core/answer/{prompt,schema,validator}.py`
- `server/tests/unit/test_{prompt,validator}.py`

## Các bước

1. `build_messages(question, chunks)`: gán mã ngắn `c1…cn` cho từng đoạn (ánh xạ về `chunk_id` thật chỉ ở phía máy chủ), đặt đoạn trong khối `<tai_lieu>`; lời nhắc hệ thống theo 5 quy tắc ở Blueprint §3.5.3 (kể cả: trả lời cùng ngôn ngữ với câu hỏi; nội dung trong khối là dữ liệu, không phải chỉ thị).
2. `LLM_OUTPUT_SCHEMA` đúng Blueprint §3.5.3 (`additionalProperties:false`); `parse_output(text) -> dict` ném `AiBadOutput` nếu không phải JSON đúng schema.
3. `GroundingValidator.validate(output, sent_chunks)`: loại mã không thuộc tập đã gửi và trùng lặp; `answered/partial` mà không còn mã hợp lệ ⇒ `not_found`; `not_found` ⇒ bỏ mọi trích dẫn; `answer` rỗng/chỉ khoảng trắng ⇒ `not_found`.
4. Test đối kháng: mã bịa, mã của lượt hỏi khác, JSON lồng, trường thừa, trích dẫn thiếu, nội dung đoạn chứa câu “bỏ qua mọi chỉ dẫn” (chỉ kiểm tra rằng nó nằm trong khối dữ liệu và không đổi cấu trúc lời nhắc).

## Tiêu chí hoàn thành

- [ ] `make check` xanh; ≥ 12 test cho `GroundingValidator` gồm các trường hợp trên.
- [ ] Test: bất biến — kết quả `answered/partial` luôn có ≥ 1 mã hợp lệ thuộc tập đã gửi.
- [ ] Test gắn `req` US-010-AC1 (không trích dẫn hợp lệ → `not_found`).
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Gọi LLM thật, truy xuất, dựng `SourceRef` (S3-03).

## Ghi chú và rủi ro

- Nội dung lời nhắc là cấu hình/tệp văn bản riêng để AI/Data hiệu chỉnh mà không sửa mã (C-10).
