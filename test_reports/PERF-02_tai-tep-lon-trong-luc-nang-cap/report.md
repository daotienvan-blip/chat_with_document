# Test report – PERF-02: Tải tệp lớn trong lúc nâng cấp

| Trường | Giá trị |
|---|---|
| Test case | [PERF-02](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.8 |
| Kết luận | **ĐẠT** |
| Bắt đầu | 2026-11-02T11:53:40.956Z |
| Kết thúc | 2026-11-02T12:02:17.675Z (516.7 s) |
| Cách thực hiện | Tự động – phần A của `rolling-test.sh` (REG-04) |
| URL ứng dụng | https://localhost:8443 |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | Tải tệp 21 MB qua proxy, dừng api-1 giữa chừng: trong lúc api-1 tắt: yêu cầu mới thành công 10/10 | 0 lỗi | ✓ | Đạt | [log](../_logs/reg04-rolling-test.log) |
| 2 | Tải tệp 21 MB qua proxy, dừng api-1 giữa chừng: yêu cầu đang chạy hoàn tất: HTTP 200, đúng sha256 | 0 lỗi | ✓ | Đạt | [log](../_logs/reg04-rolling-test.log) |
| 3 | Tải tệp 21 MB qua proxy, dừng api-1 giữa chừng: api-1 thoát mã 0 | 0 lỗi | ✓ | Đạt | [log](../_logs/reg04-rolling-test.log) |

## Log

- [reg04-rolling-test.log](../_logs/reg04-rolling-test.log)

## Ghi chú / lỗi phát hiện

- Kế hoạch ghi 23 MB; lượt này dùng tệp 21 MB do agent sinh.
