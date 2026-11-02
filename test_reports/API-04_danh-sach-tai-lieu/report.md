# Test report – API-04: Danh sách tài liệu

| Trường | Giá trị |
|---|---|
| Test case | [API-04](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.4 |
| Mục tiêu (test plan) | `GET /documents`: danh sách, thứ tự, trạng thái |
| Kết luận | **ĐẠT** |
| Bắt đầu | 2026-11-02T12:15:50.108Z |
| Kết thúc | 2026-11-02T12:15:51.092Z (1.0 s) |
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
| 1 | `test_upload_list_get` (integration/test_flows) | Test đạt | passed (0.37 s) | Đạt | [log](logs/01-pytest.log) |

## Log

- [01-pytest.log](logs/01-pytest.log)

## Ghi chú / lỗi phát hiện

- (không có)
