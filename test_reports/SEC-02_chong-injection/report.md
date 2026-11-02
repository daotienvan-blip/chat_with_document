# Test report – SEC-02: Chống injection

| Trường | Giá trị |
|---|---|
| Test case | [SEC-02](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.9 |
| Mục tiêu (test plan) | SQL tham số hóa; tsquery chỉ ghép từ chữ/số; khối tài liệu được đánh dấu "là dữ liệu" trong lời nhắc |
| Kết luận | **ĐẠT** |
| Bắt đầu | 2026-11-02T12:16:00.467Z |
| Kết thúc | 2026-11-02T12:16:00.847Z (0.4 s) |
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
| 1 | `test_tsquery_safe[\u0110i\u1ec1u kho\u1ea3n 'thanh to\xe1n' & ph\u1ea1t \| ! : * ( )]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 2 | `test_tsquery_safe[]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 3 | `test_tsquery_safe[???]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 4 | `test_tsquery_safe[a_b ca_b ca_b ca_b ca_b ca_b ca_b ca_b ca_b ca_b ca_b ca_b ca_b ca_b ca…` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 5 | `test_prompt_marks_data_block` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |

## Log

- [01-pytest.log](logs/01-pytest.log)

## Ghi chú / lỗi phát hiện

- (không có)
