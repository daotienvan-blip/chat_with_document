# Test report – UI-03: Trạng thái thành phần

| Trường | Giá trị |
|---|---|
| Test case | [UI-03](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.11 |
| Mục tiêu (test plan) | Trống, đang tải (tiến độ), đang xử lý, sẵn sàng, lỗi, đang chờ trả lời, lỗi AI có đếm ngược |
| Kết luận | **CẦN NGƯỜI XÁC NHẬN** |
| Bắt đầu | 2026-11-02T12:16:17.538Z |
| Kết thúc | 2026-11-02T12:16:19.306Z (1.8 s) |
| Cách thực hiện | Tự động – vitest + Testing Library trên jsdom, chạy riêng các test của case này |
| URL ứng dụng | — |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |
| Thư mục chạy | app/web |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | `[US-006-AC2] kho trống: hướng dẫn tải và khóa khung hỏi` (src/app/app.test.tsx) | Test đạt | passed (0.07 s) | Đạt | [log](logs/01-vitest.log) |
| 2 | `[US-002-AC2][US-003-AC2] trạng thái có chữ, lý do lỗi và tài liệu chưa sẵn sàng` (src/app/app.test.tsx) | Test đạt | passed (0.01 s) | Đạt | [log](logs/01-vitest.log) |
| 3 | `[US-006-AC1][US-007-AC1][US-008-AC1] hỏi, hiển thị nguồn dạng chip mở đúng trang; giữ qua…` (src/app/app.test.tsx) | Test đạt | passed (0.13 s) | Đạt | [log](logs/01-vitest.log) |
| 4 | `[US-010-AC1][US-010-AC2] không tìm thấy và trả lời một phần có kiểu hiển thị riêng` (src/app/app.test.tsx) | Test đạt | passed (0.09 s) | Đạt | [log](logs/01-vitest.log) |
| 5 | `[EC-07] lỗi AI giữ câu hỏi, đếm ngược Retry-After rồi gửi lại` (src/app/app.test.tsx) | Test đạt | passed (0.15 s) | Đạt | [log](logs/01-vitest.log) |
| 6 | Kiểm các trạng thái trên trình duyệt thật, gồm "đang tải (tiến độ)" | Trống, đang tải, đang xử lý, sẵn sàng, lỗi, chờ trả lời, lỗi AI có đếm ngược | Chưa chạy trên trình duyệt thật: dự án chưa có Playwright (S8-08). Cần người kiểm thử mở ứng dụng và xác nhận. | Cần người xác nhận | — |

## Log

- [01-vitest.log](logs/01-vitest.log)

## Ghi chú / lỗi phát hiện

- Test thành phần chưa phủ trạng thái "đang tải (tiến độ)" khi tải tệp lên.
