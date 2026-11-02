# Test report – E2E-02: Hỏi trên nhiều tài liệu

| Trường | Giá trị |
|---|---|
| Test case | [E2E-02](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.5 |
| Kết luận | **CẦN NGƯỜI XÁC NHẬN** |
| Bắt đầu | 2026-11-02T11:51:27.101Z |
| Kết thúc | 2026-11-02T11:51:29.894Z (2.8 s) |
| Cách thực hiện | Bán tự động – `smoke.py` (HTTP); bước trình duyệt chưa chạy |
| URL ứng dụng | http://localhost:8010 — bản api + worker riêng cho lượt này: CSDL `cwd_smoke`, kho tệp riêng, `LLM_PROVIDER=extractive` |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | Tải thêm bao-gia-B.pdf | 202 | tải lên bao-gia-B.pdf → 202 processing | Đạt | [log](../_logs/reg03-smoke.log) |
| 2 | Tải thêm quy-dinh-C.pdf | 202 | tải lên quy-dinh-C.pdf → 202 processing | Đạt | [log](../_logs/reg03-smoke.log) |
| 3 | Hỏi so sánh thời hạn thanh toán | Nguồn liệt kê A và B | câu hỏi nhiều tài liệu → partial, nguồn ['hop-dong-A.pdf', 'bao-gia-B.pdf'] | Đạt | [log](../_logs/reg03-smoke.log) |
| 4 | Lặp lại trên trình duyệt thật | Nguồn liệt kê A và B | Chưa chạy trên trình duyệt thật: dự án chưa có Playwright (S8-08). Cần người kiểm thử mở ứng dụng và xác nhận. | Cần người xác nhận | — |

## Log

- [reg03-smoke.log](../_logs/reg03-smoke.log)

## Ghi chú / lỗi phát hiện

- (không có)
