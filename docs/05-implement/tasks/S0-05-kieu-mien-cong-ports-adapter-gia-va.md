# S0-05 — Kiểu miền, cổng (ports), adapter giả và composition root

| | |
|---|---|
| **Lát cắt** | S0 — Khung chạy được (walking skeleton) (mốc M0) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S0-03](S0-03-nen-tang-server-cau-hinh-log-loi-problem.md) |
| **Truy vết** | QAS-06, QAS-07 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Cổng, kiểu miền, `FakeLlm`, kho bộ nhớ, composition root (`cwd_server/container.py`) |

## Mục tiêu

Có toàn bộ hợp đồng nội bộ và các adapter giả đủ để kiểm thử logic nghiệp vụ không cần mạng; một nơi duy nhất nối adapter vào lõi.

## Đọc trước

- Blueprint §3.2.1–§3.2.3, §3.3.1
- SAD §2.2.1
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/cwd_server/ports/{llm,object_store,pdf_extractor,repositories}.py`
- `server/cwd_server/core/types.py` (Document, Chunk, RetrievedChunk, SourceRef, AnswerResult, Job và enum)
- `server/cwd_server/core/errors.py` (AiUnavailable, AiTimeout, AiBadOutput, PdfCorrupt, PdfEncrypted, StorageUnavailable, FileTooLarge, UnsupportedType…)
- `server/cwd_server/adapters/{llm_fake,memory_store}.py`
- `server/cwd_server/api/container.py`

## Các bước

1. Định nghĩa `Protocol` đúng chữ ký ở Blueprint §3.2.2 (kể cả `ObjectStorePort.get(key, byte_range=None)`).
2. `FakeLlm`: `embed` băm từng từ vào vector D chiều rồi chuẩn hóa (độ tương tự cosin phản ánh trùng từ → kiểm thử truy xuất có ý nghĩa); `generate` trả bản ghi kịch bản do test đặt và có chế độ gây lỗi (`AiUnavailable`/`AiTimeout`/đầu ra sai).
3. `InMemoryObjectStore` (hỗ trợ range, xóa idempotent, liệt kê khóa).
4. `build_container(settings)` chọn adapter theo `LLM_PROVIDER=fake|http`, `OBJECT_STORE=memory|s3`; chỉ chỗ này được import adapter.

## Tiêu chí hoàn thành

- [ ] `make check` xanh.
- [ ] Test: `FakeLlm.embed` cho độ tương tự cao hơn với văn bản chung từ hơn; cùng đầu vào → cùng vector.
- [ ] Test: `InMemoryObjectStore.get` với range trả đúng byte; `delete` hai lần không lỗi.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Chưa có adapter S3 (S0-06) hay HTTP (S3-04).
- Chưa có repository thật.

## Ghi chú và rủi ro

- Kiểu miền phải khớp `openapi.yaml` ở các tên enum (`DocumentStatus`, `FailureReason`, `AnswerStatus`).
