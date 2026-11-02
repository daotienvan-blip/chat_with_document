# Test report – SEC-06: Kiểm soát truy cập mạng

| Trường | Giá trị |
|---|---|
| Test case | [SEC-06](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.9 |
| Mục tiêu (test plan) | Allowlist dải nội bộ; `/metrics` chỉ cho 10/8 ⇒ 403 ngoài allowlist |
| Kết luận | **ĐẠT** |
| Bắt đầu | 2026-11-02T11:52:59.747Z |
| Kết thúc | 2026-11-02T12:02:17.675Z (557.9 s) |
| Cách thực hiện | Tự động – `proxy-test.sh` (REG-04) |
| URL ứng dụng | https://localhost:8443 |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | /metrics từ máy dev | 403 | /metrics từ máy dev → 403 | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 2 | Truy cập từ dải ngoài allowlist (100.64.10.0/24) | 403 | truy cập từ 100.64.10.0/24 (ngoài allowlist) → 403 (nhận: 403) | Đạt | [log](../_logs/reg04-proxy-test.log) |

## Log

- [reg04-proxy-test.log](../_logs/reg04-proxy-test.log)

## Ghi chú / lỗi phát hiện

- (không có)
