# Test report – E2E-01: Tải, chờ sẵn sàng, hỏi

| Trường | Giá trị |
|---|---|
| Test case | [E2E-01](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.5 |
| Kết luận | **CẦN NGƯỜI XÁC NHẬN** |
| Bắt đầu | 2026-11-02T11:51:27.101Z |
| Kết thúc | 2026-11-02T11:51:29.894Z (2.8 s) |
| Cách thực hiện | Bán tự động – `smoke.py` (HTTP) + test thành phần web; bước trình duyệt chưa chạy |
| URL ứng dụng | http://localhost:8010 — bản api + worker riêng cho lượt này: CSDL `cwd_smoke`, kho tệp riêng, `LLM_PROVIDER=extractive` |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | Tải hop-dong-A.pdf | 202, trạng thái processing | tải lên hop-dong-A.pdf → 202 processing | Đạt | [log](../_logs/reg03-smoke.log) |
| 2 | Chờ sẵn sàng | Trạng thái ready | hop-dong-A.pdf sẵn sàng (2 trang) | Đạt | [log](../_logs/reg03-smoke.log) |
| 3 | Hỏi điều khoản thanh toán | answered | hỏi có căn cứ → answered | Đạt | [log](../_logs/reg03-smoke.log) |
| 4 | Kiểm tra nguồn | Nguồn hop-dong-A.pdf có trang 1 | nguồn: hop-dong-A.pdf tr. [1, 2] | Đạt | [log](../_logs/reg03-smoke.log) |
| 5 | Mở tài liệu nguồn | Trả nội dung theo Range | mở tài liệu nguồn (Range) | Đạt | [log](../_logs/reg03-smoke.log) |
| 6 | Chip nguồn mở PDF đúng trang (test thành phần web, jsdom) | Đạt | `[US-006-AC1][US-007-AC1][US-008-AC1]` đạt ở REG-01 | Đạt | [log](../REG-01_hoi-quy-don-vi-server-va-web/logs/02-vitest.log) |
| 7 | Lặp lại trên trình duyệt thật | Câu trả lời có nguồn hop-dong-A.pdf trang 1; chip mở PDF đúng trang | Chưa chạy trên trình duyệt thật: dự án chưa có Playwright (S8-08). Cần người kiểm thử mở ứng dụng và xác nhận. | Cần người xác nhận | — |

## Log

- [reg03-smoke.log](../_logs/reg03-smoke.log)

## Ghi chú / lỗi phát hiện

- (không có)
