# Test report – PERF-05: Thời gian build CI

| Trường | Giá trị |
|---|---|
| Test case | [PERF-05](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.8 |
| Kết luận | **ĐẠT** |
| Bắt đầu | 2026-11-02T11:49:31.000Z |
| Kết thúc | 2026-11-02T11:49:51.000Z (20.0 s) |
| Cách thực hiện | Tự động – đo trong L0 |
| URL ứng dụng | — |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | Tổng thời gian L0 cục bộ (`make ci`) | < 10 phút | 20 s | Đạt | [log](../_logs/l0-ci.log) |
| 2 | Job chậm nhất trên GitHub Actions (mỗi job giới hạn 10 phút) | < 10 phút | server · lint + type + test + coverage: 56 s | Đạt | [log](../_logs/l0-github-actions.json) |

## Log

- [l0-ci.log](../_logs/l0-ci.log)
- [l0-github-actions.json](../_logs/l0-github-actions.json)

## Ghi chú / lỗi phát hiện

- (không có)
