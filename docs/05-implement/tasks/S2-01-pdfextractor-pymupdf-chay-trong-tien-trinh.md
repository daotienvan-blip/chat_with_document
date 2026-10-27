# S2-01 — PdfExtractor (PyMuPDF) chạy trong tiến trình con có giới hạn

| | |
|---|---|
| **Lát cắt** | S2 — Xử lý tài liệu đến khi sẵn sàng hoặc lỗi (UC09, UC10) (mốc M1) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S0-05](S0-05-kieu-mien-cong-ports-adapter-gia-va.md) |
| **Truy vết** | UC09, UC10, US-003-AC1, US-003-AC2, US-003-AC3, ASM-001 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Tiến trình con có hạn thời gian. Giới hạn bộ nhớ **chưa kiểm chứng** trên macOS |

## Mục tiêu

Trích văn bản theo trang từ PDF không tin cậy, phân biệt rõ hỏng / có mật khẩu / không có văn bản, và không thể treo hay làm cạn bộ nhớ của worker.

## Đọc trước

- Blueprint §3.2.2, §3.8.2
- SAD §4.1 (Cô lập xử lý PDF)
- API_Design §3.2.2 (FailureReason)
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/cwd_server/adapters/pymupdf_extractor.py`
- `server/tests/fixtures/pdfs.py` (sinh PDF mẫu bằng mã)
- `server/tests/integration/test_pdf_extractor.py`

## Các bước

1. `extract(stream, limits) -> list[Page(number≥1, text)]`; chạy trong tiến trình con riêng với hạn thời gian `[Đề xuất]` 120 s và giới hạn bộ nhớ; quá hạn → kết thúc tiến trình con và ném `PdfCorrupt`-tương-đương `PdfTimeout` (ánh xạ về lỗi xử lý tạm thời, không phải lỗi nội dung).
2. Ném `PdfEncrypted` nếu cần mật khẩu; `PdfCorrupt` nếu không mở được.
3. Sinh fixture trong mã (không commit PDF nhị phân lớn): PDF nhiều trang chứa token duy nhất mỗi trang, PDF mã hóa, PDF cắt cụt, PDF chỉ có ảnh.
4. Trang không có văn bản trả `text=''` (quyết định “không có văn bản” thuộc `IngestionService`, S2-04).

## Tiêu chí hoàn thành

- [ ] `make test-int` xanh; test cho đủ 4 fixture, số trang bắt đầu từ 1 và khớp token.
- [ ] Test: tiến trình con bị kết thúc khi vượt hạn (dùng hạn rất ngắn trong test).
- [ ] Test: bộ nhớ của tiến trình chính không tăng đáng kể với PDF 100 trang (kiểm tra thô).
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Chia đoạn (S2-02).

## Ghi chú và rủi ro

- Giới hạn bộ nhớ qua `resource.setrlimit` trong tiến trình con có thể không áp dụng trên macOS; kiểm tra trên Linux/container và ghi rõ trong docstring.
