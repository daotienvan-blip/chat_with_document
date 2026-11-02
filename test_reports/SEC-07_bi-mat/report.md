# Test report – SEC-07: Bí mật

| Trường | Giá trị |
|---|---|
| Test case | [SEC-07](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.9 |
| Mục tiêu (test plan) | gitleaks toàn bộ lịch sử git; bí mật chỉ nằm trong tệp bị gitignore ⇒ 0 phát hiện |
| Kết luận | **ĐẠT** |
| Bắt đầu | 2026-11-02T12:13:58.782Z |
| Kết thúc | 2026-11-02T12:13:59.112Z (0.3 s) |
| Cách thực hiện | Tự động – lệnh kiểm tra (xem log) |
| URL ứng dụng | — |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |
| Thư mục chạy | . |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | gitleaks toàn bộ lịch sử git | Không phát hiện bí mật | Mã thoát 0: 7:13PM INF 13 commits scanned.; 7:13PM INF no leaks found | Đạt | [log](logs/01-shell.log) |
| 2 | Tệp chứa bí mật nằm ngoài git | 3/3 tệp bị gitignore, 0 tệp được theo dõi | Mã thoát 0: Tệp chứa bí mật bị gitignore: 3/3; đang được git theo dõi: 0 | Đạt | [log](logs/02-shell.log) |

## Log

- [01-shell.log](logs/01-shell.log)
- [02-shell.log](logs/02-shell.log)

## Ghi chú / lỗi phát hiện

- (không có)
