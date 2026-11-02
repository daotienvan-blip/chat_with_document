# Test report – SEC-09: Chống lạm dụng tài nguyên

| Trường | Giá trị |
|---|---|
| Test case | [SEC-09](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.9 |
| Mục tiêu (test plan) | Giới hạn tốc độ, LoadGuard, giới hạn kích thước thân yêu cầu ⇒ 429/503/413 |
| Kết luận | **ĐẠT** |
| Bắt đầu | 2026-11-02T12:16:02.536Z |
| Kết thúc | 2026-11-02T12:16:03.530Z (1.0 s) |
| Cách thực hiện | Tự động – pytest, chạy riêng các test của case này |
| URL ứng dụng | — |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |
| Thư mục chạy | app/server |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | `test_busy_and_rate_limit` (integration/test_flows) | Test đạt | passed (0.30 s) | Đạt | [log](logs/01-pytest.log) |
| 2 | `test_load_guard_busy_after_wait` (unit/test_core_units) | Test đạt | passed (0.05 s) | Đạt | [log](logs/01-pytest.log) |
| 3 | `test_rate_limiter_bucket_and_recovery` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 4 | Thân yêu cầu quá lớn qua proxy | 413 FILE_TOO_LARGE problem+json | 413 → problem+json FILE_TOO_LARGE có requestId | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 5 | Vượt hạn mức câu hỏi qua proxy | 429 RATE_LIMITED, có Retry-After | 429 sau 6 yêu cầu → problem+json RATE_LIMITED, có Retry-After | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 6 | Câu hỏi 100 KB qua proxy | 400 QUESTION_TOO_LONG | câu hỏi 100 KB → proxy trả 400 QUESTION_TOO_LONG problem+json | Đạt | [log](../_logs/reg04-proxy-test.log) |

## Log

- [01-pytest.log](logs/01-pytest.log)
- [reg04-proxy-test.log](../_logs/reg04-proxy-test.log)

## Ghi chú / lỗi phát hiện

- (không có)
