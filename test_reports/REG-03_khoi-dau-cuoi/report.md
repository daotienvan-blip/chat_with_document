# Test report – REG-03: Khói đầu-cuối

| Trường | Giá trị |
|---|---|
| Test case | [REG-03](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.7 |
| Kết luận | **ĐẠT** |
| Bắt đầu | 2026-11-02T11:51:27.101Z |
| Kết thúc | 2026-11-02T11:51:29.894Z (2.8 s) |
| Cách thực hiện | Tự động – `server/scripts/smoke.py` (HTTP) |
| URL ứng dụng | http://localhost:8010 — bản api + worker riêng cho lượt này: CSDL `cwd_smoke`, kho tệp riêng, `LLM_PROVIDER=extractive` |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | readyz | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg03-smoke.log) |
| 2 | phục vụ giao diện web | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg03-smoke.log) |
| 3 | tải lên hop-dong-A.pdf → 202 processing | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg03-smoke.log) |
| 4 | tải lên bao-gia-B.pdf → 202 processing | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg03-smoke.log) |
| 5 | tải lên quy-dinh-C.pdf → 202 processing | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg03-smoke.log) |
| 6 | hop-dong-A.pdf sẵn sàng (2 trang) | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg03-smoke.log) |
| 7 | bao-gia-B.pdf sẵn sàng (1 trang) | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg03-smoke.log) |
| 8 | quy-dinh-C.pdf sẵn sàng (1 trang) | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg03-smoke.log) |
| 9 | hỏi có căn cứ → answered | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg03-smoke.log) |
| 10 | nguồn: hop-dong-A.pdf tr. [1, 2] | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg03-smoke.log) |
| 11 | mở tài liệu nguồn (Range) | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg03-smoke.log) |
| 12 | câu hỏi nhiều tài liệu → partial, nguồn ['hop-dong-A.pdf', 'bao-gia-B.pdf'] | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg03-smoke.log) |
| 13 | câu ngoài tài liệu → not_found, không nguồn | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg03-smoke.log) |
| 14 | PDF có mật khẩu → FILE_ENCRYPTED | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg03-smoke.log) |
| 15 | tệp không phải PDF → 400 UNSUPPORTED_TYPE | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg03-smoke.log) |
| 16 | xóa quy-dinh-C.pdf → 204 | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg03-smoke.log) |
| 17 | sau khi xóa, không còn nguồn từ tài liệu đã xóa | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg03-smoke.log) |

## Log

- [reg03-smoke.log](../_logs/reg03-smoke.log)
- [reg03-worker.log](../_logs/reg03-worker.log)
- [reg03-api.log](../_logs/reg03-api.log)

## Ghi chú / lỗi phát hiện

- Chạy trên một bản cô lập để không đụng dữ liệu demo `cwd`. CSDL `cwd_smoke` và kho tệp đã được xóa sau khi chạy; log được giữ ở `_logs/`.
