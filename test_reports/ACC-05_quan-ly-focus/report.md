# Test report – ACC-05: Quản lý focus

| Trường | Giá trị |
|---|---|
| Test case | [ACC-05](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.10 |
| Mục tiêu (test plan) | Hộp thoại xóa: focus vào Hủy, Esc đóng, trả focus về nút mở |
| Kết luận | **CẦN NGƯỜI XÁC NHẬN** |
| Bắt đầu | 2026-11-02T12:16:14.111Z |
| Kết thúc | 2026-11-02T12:16:16.045Z (1.9 s) |
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
| 1 | `[US-005-AC1] hộp thoại xóa: focus vào Hủy, Esc đóng, xác nhận gọi DELETE` (src/app/app.test.tsx) | Test đạt | passed (0.15 s) | Đạt | [log](logs/01-vitest.log) |
| 2 | Lặp lại trên trình duyệt thật | Focus vào Hủy, Esc đóng, trả focus về nút mở | Chưa chạy trên trình duyệt thật: dự án chưa có Playwright (S8-08). Cần người kiểm thử mở ứng dụng và xác nhận. | Cần người xác nhận | — |

## Log

- [01-vitest.log](logs/01-vitest.log)

## Ghi chú / lỗi phát hiện

- (không có)
