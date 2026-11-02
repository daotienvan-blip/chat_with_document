# Test report – UI-04: Ánh xạ lỗi

| Trường | Giá trị |
|---|---|
| Test case | [UI-04](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.11 |
| Mục tiêu (test plan) | Bảng ánh xạ `uiErrors.ts`: mã lạ ⇒ lỗi chung có mã tham chiếu |
| Kết luận | **ĐẠT** |
| Bắt đầu | 2026-11-02T12:16:19.307Z |
| Kết thúc | 2026-11-02T12:16:20.645Z (1.3 s) |
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
| 1 | `ánh xạ lỗi: mã lạ ⇒ lỗi chung có mã tham chiếu; lỗi trường không thử lại` (src/app/app.test.tsx) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-vitest.log) |

## Log

- [01-vitest.log](logs/01-vitest.log)

## Ghi chú / lỗi phát hiện

- (không có)
