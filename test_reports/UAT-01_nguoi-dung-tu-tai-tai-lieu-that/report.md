# Test report – UAT-01: Người dùng tự tải tài liệu thật

| Trường | Giá trị |
|---|---|
| Test case | [UAT-01](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.6 |
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
| 1 | Người dùng tự tải 5 tài liệu thật, gồm 1 tệp lỗi | Hiểu được trạng thái và lý do lỗi không cần hướng dẫn | Cần business owner và người dùng thật thực hiện, ký biên bản UAT (L4); bộ tài liệu thật DEP-002; OQ-004 (ngưỡng G3) và OQ-005 (dữ liệu thật, AI thật) chưa đóng. Agent không thể thay thế. | Bị chặn | — |

## Log

- (không có)

## Ghi chú / lỗi phát hiện

- Luồng tương ứng đã chạy tự động trên bản demo ở REG-03, REG-05 và E2E-01…05.
