# Test report – PERF-01: Độ trễ truy xuất vector

| Trường | Giá trị |
|---|---|
| Test case | [PERF-01](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.8 |
| Kết luận | **ĐẠT** |
| Bắt đầu | 2026-11-02T12:06:53Z |
| Kết thúc | 2026-11-02T12:13:56Z (423.0 s) |
| Cách thực hiện | Tự động – `scripts/spike_hnsw.py` trên CSDL riêng `cwd_spike` (đã migrate 384 chiều, xóa sau khi chạy) |
| URL ứng dụng | — |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | Nạp dữ liệu thử | 40.000 đoạn, 384 chiều | 40000 đoạn, 384 chiều, 417.0 s | Đạt | [log](../_logs/perf01-spike.log) |
| 2 | p95 truy vấn vector, chế độ `exact` (đang dùng trong cấu hình) | ≤ 100 ms (đề xuất) | p50 25.5 ms, p95 28.9 ms | Đạt | [log](../_logs/perf01-spike.log) |

## Log

- [perf01-spike.log](../_logs/perf01-spike.log)

## Ghi chú / lỗi phát hiện

- PostgreSQL 17.11 (Homebrew), pgvector 0.8.7.
- Lần chạy đầu trên CSDL chưa có lược đồ bị lỗi (script đọc số chiều từ bảng `chunks`); đã migrate rồi chạy lại.
- Bảng đầy đủ các chế độ HNSW (ef_search, recall) nằm trong log.
