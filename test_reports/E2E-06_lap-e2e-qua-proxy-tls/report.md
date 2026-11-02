# Test report – E2E-06: Lặp E2E qua proxy TLS

| Trường | Giá trị |
|---|---|
| Test case | [E2E-06](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.5 |
| Kết luận | **BỊ CHẶN** |
| Bắt đầu | 2026-11-02T11:52:59.747Z |
| Kết thúc | 2026-11-02T11:52:59.747Z (0.0 s) |
| Cách thực hiện | Không thực thi đầy đủ – thiếu công cụ phù hợp |
| URL ứng dụng | https://localhost:8443 |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | Tiêu đề bảo mật qua proxy | CSP, nosniff, no-referrer | CSP, nosniff, no-referrer đạt (HSTS thiếu — xem SEC-05) | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 2 | Lặp E2E-01…05 qua https://localhost:8443 | Như E2E-01…05 | Chưa chạy: `smoke.py` giả định kho tài liệu trống và so theo tên tệp, trong khi stack prod cục bộ đang có 7 tài liệu cũ; smoke còn tải 5 tệp liên tiếp nên vượt giới hạn tải lên của proxy (burst 3, 10/phút) — đã gặp 429 ngày 29/10. Cần sửa smoke (so theo id, g… | Bị chặn | — |

## Log

- [reg04-proxy-test.log](../_logs/reg04-proxy-test.log)

## Ghi chú / lỗi phát hiện

- (không có)
