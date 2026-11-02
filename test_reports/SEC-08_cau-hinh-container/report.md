# Test report – SEC-08: Cấu hình container

| Trường | Giá trị |
|---|---|
| Test case | [SEC-08](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.9 |
| Mục tiêu (test plan) | Không chạy root, `read_only`, `no-new-privileges`, worker không ra Internet |
| Kết luận | **ĐẠT** |
| Bắt đầu | 2026-11-02T12:13:59.113Z |
| Kết thúc | 2026-11-02T12:13:59.424Z (0.3 s) |
| Cách thực hiện | Tự động – lệnh kiểm tra (xem log) |
| URL ứng dụng | Stack `make prod-up` (container cwd-prod-*) |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |
| Thư mục chạy | app |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | Cấu hình container (docker inspect) | api, worker, proxy không chạy root, read_only, no-new-privileges; worker chỉ nối mạng internal | Mã thoát 0: cwd-prod-api-1: user=10001 read_only=true security_opt=[no-new-privileges:true]; cwd-prod-api-2: user=10001 read_only=true security_opt=[no-new-privileges:true]; cwd-prod-worker-1: user=10001 read_only=true security_opt=[no-new-privileges:true]; c… | Đạt | [log](logs/01-shell.log) |

## Log

- [01-shell.log](logs/01-shell.log)

## Ghi chú / lỗi phát hiện

- Container `db` dùng ảnh `pgvector/pgvector:pg17` nguyên bản, không thuộc phạm vi kiểm này.
