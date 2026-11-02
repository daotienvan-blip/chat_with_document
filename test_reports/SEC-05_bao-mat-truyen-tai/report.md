# Test report – SEC-05: Bảo mật truyền tải

| Trường | Giá trị |
|---|---|
| Test case | [SEC-05](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.9 |
| Mục tiêu (test plan) | TLS ≥ 1.2, HSTS, CSP, nosniff, no-referrer, `server_tokens off` |
| Kết luận | **KHÔNG ĐẠT** |
| Bắt đầu | 2026-11-02T12:13:58.703Z |
| Kết thúc | 2026-11-02T12:13:58.781Z (0.1 s) |
| Cách thực hiện | Tự động – lệnh kiểm tra (xem log) |
| URL ứng dụng | https://localhost:8443 |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |
| Thư mục chạy | app |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | TLS 1.2+ được chấp nhận | Kết nối thành công | TLS 1.2+ được chấp nhận | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 2 | TLS 1.1 bị từ chối | Kết nối thất bại | TLS 1.1 bị từ chối | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 3 | CSP | default-src 'self'; frame-ancestors 'none' | CSP default-src 'self'; frame-ancestors 'none' | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 4 | X-Content-Type-Options | nosniff | X-Content-Type-Options: nosniff | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 5 | Referrer-Policy | no-referrer | Referrer-Policy: no-referrer | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 6 | `server_tokens off` | Tiêu đề Server không có số phiên bản | Server không lộ phiên bản (Server: nginx) | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 7 | Tiêu đề HSTS qua proxy | Có tiêu đề Strict-Transport-Security | Mã thoát 1: KHÔNG có tiêu đề Strict-Transport-Security | Không đạt | [log](logs/01-shell.log) |

## Log

- [reg04-proxy-test.log](../_logs/reg04-proxy-test.log)
- [01-shell.log](logs/01-shell.log)

## Ghi chú / lỗi phát hiện

- **Lỗi mới DEF-005:** proxy không gửi `Strict-Transport-Security`. `proxy-test.sh` không kiểm HSTS nên REG-04 vẫn 15/15 — xem README, mục Lỗi phát hiện.
