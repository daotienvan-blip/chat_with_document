# Test report – UI-01: So sánh với thiết kế

| Trường | Giá trị |
|---|---|
| Test case | [UI-01](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.11 |
| Kết luận | **BỊ CHẶN** |
| Bắt đầu | — |
| Kết thúc | — |
| Cách thực hiện | Không thực thi – bị chặn |
| URL ứng dụng | — |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | So với `docs/04-design/html_design/` | Bố cục và chữ trên nút khớp; khác biệt được ghi lại | Chưa chạy: cần trình duyệt và người so sánh. | Bị chặn | — |

## Log

- (không có)

## Ghi chú / lỗi phát hiện

- (không có)
