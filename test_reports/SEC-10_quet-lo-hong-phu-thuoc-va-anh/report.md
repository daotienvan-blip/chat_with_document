# Test report – SEC-10: Quét lỗ hổng phụ thuộc và ảnh

| Trường | Giá trị |
|---|---|
| Test case | [SEC-10](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.9 |
| Mục tiêu (test plan) | `pip-audit`, `npm audit`, quét ảnh ⇒ 0 lỗ hổng mức high/critical (G9) |
| Kết luận | **KHÔNG ĐẠT** |
| Bắt đầu | 2026-11-02T12:16:03.531Z |
| Kết thúc | 2026-11-02T12:16:14.108Z (10.6 s) |
| Cách thực hiện | Tự động – lệnh kiểm tra (xem log) |
| URL ứng dụng | — |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |
| Thư mục chạy | app/server; app/web |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | npm audit (web, mọi phụ thuộc kể cả dev) | 0 lỗ hổng mức high/critical | Mã thoát 1: 12 vulnerabilities (8 moderate, 1 high, 3 critical) | Không đạt | [log](logs/01-shell.log) |
| 2 | npm audit (web, chỉ phụ thuộc runtime) | 0 lỗ hổng mức high/critical | Mã thoát 0: found 0 vulnerabilities | Đạt | [log](logs/02-shell.log) |
| 3 | pip-audit (server, phụ thuộc đã cài trong .venv) | 0 lỗ hổng đã biết | Mã thoát 0: No known vulnerabilities found | Đạt | [log](logs/04-shell.log) |
| 4 | Quét lỗ hổng ảnh Docker (`cwd-server`, `cwd-web`) | 0 mức high/critical | Chưa chạy: máy chưa có công cụ quét ảnh (trivy hoặc grype); agent không tự cài công cụ hệ thống. | Bị chặn | — |

## Log

- [01-shell.log](logs/01-shell.log)
- [02-shell.log](logs/02-shell.log)
- [03-setup.log](logs/03-setup.log)
- [04-shell.log](logs/04-shell.log)

## Ghi chú / lỗi phát hiện

- pip-audit được cài vào một venv tạm ngoài dự án; không đổi `.venv` của dự án.
- **Lỗi mới DEF-006:** 12 lỗ hổng trong phụ thuộc dev của web (8 moderate, 1 high, 3 critical) — vitest, vite, esbuild, tinypool, glob, minimatch. Phụ thuộc runtime: 0. Bản sửa cần nâng phiên bản chính (vitest 5, vite 8) — xem README.
