# Test report – SEC-01: Tệp tải lên không tin cậy

| Trường | Giá trị |
|---|---|
| Test case | [SEC-01](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.9 |
| Mục tiêu (test plan) | Magic bytes, giới hạn kích thước, làm sạch tên; trích PDF trong tiến trình con có hạn thời gian/bộ nhớ ⇒ từ chối hoặc đánh dấu lỗi, không treo worker |
| Kết luận | **ĐẠT** |
| Bắt đầu | 2026-11-02T12:15:57.965Z |
| Kết thúc | 2026-11-02T12:16:00.466Z (2.5 s) |
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
| 1 | `test_upload_rejects_non_pdf[%PDF-1.7\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx…` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 2 | `test_upload_rejects_non_pdf[MZ\x90\x00xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-…` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 3 | `test_upload_rejects_non_pdf[-rong.pdf]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 4 | `test_upload_exact_limit_ok_one_byte_over_rejected` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 5 | `test_sanitize_name[../../etc/passwd.pdf-passwd.pdf]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 6 | `test_sanitize_name[C:\\x\\h\u1ee3p \u0111\u1ed3ng.pdf-h\u1ee3p \u0111\u1ed3ng.pdf]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 7 | `test_sanitize_name[-tai-lieu.pdf]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 8 | `test_sanitize_name[a\x00b.pdf-ab.pdf]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 9 | `test_pdf_extractor_cases` (unit/test_adapters) | Test đạt | passed (0.89 s) | Đạt | [log](logs/01-pytest.log) |
| 10 | `test_pdf_extractor_crash_is_not_corrupt[1-Traceback (most recent call last):\n  ...\nMemo…` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 11 | `test_pdf_extractor_crash_is_not_corrupt[1-ImportError: lib.so: failed to map segment from…` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 12 | `test_pdf_extractor_crash_is_not_corrupt[-9--SIGKILL]` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 13 | `test_pdf_extractor_crash_is_not_corrupt[3-van ban tai lieu-exit3]` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 14 | `test_ingestion_outcomes[ready]` (integration/test_flows) | Test đạt | passed (0.34 s) | Đạt | [log](logs/01-pytest.log) |
| 15 | `test_ingestion_outcomes[corrupt]` (integration/test_flows) | Test đạt | passed (0.15 s) | Đạt | [log](logs/01-pytest.log) |
| 16 | `test_ingestion_outcomes[encrypted]` (integration/test_flows) | Test đạt | passed (0.19 s) | Đạt | [log](logs/01-pytest.log) |
| 17 | `test_ingestion_outcomes[image-only]` (integration/test_flows) | Test đạt | passed (0.17 s) | Đạt | [log](logs/01-pytest.log) |
| 18 | `test_ingestion_extractor_crash_is_processing_error` (integration/test_flows) | Test đạt | passed (0.04 s) | Đạt | [log](logs/01-pytest.log) |

## Log

- [01-pytest.log](logs/01-pytest.log)

## Ghi chú / lỗi phát hiện

- (không có)
