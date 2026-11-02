# Test report – PERF-04: Thời gian tài liệu sẵn sàng

| Trường | Giá trị |
|---|---|
| Test case | [PERF-04](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.8 |
| Kết luận | **BỊ CHẶN** |
| Bắt đầu | 2026-11-02T11:51:27.101Z |
| Kết thúc | 2026-11-02T11:51:29.894Z (2.8 s) |
| Cách thực hiện | Đo trong lượt REG-03; không có ngưỡng |
| URL ứng dụng | http://localhost:8010 — bản api + worker riêng cho lượt này: CSDL `cwd_smoke`, kho tệp riêng, `LLM_PROVIDER=extractive` |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | Đo `durationMs` của sự kiện `document_ready` (3 PDF mẫu, lượt REG-03) | ≤ [TBD: OQ-P07] | Đo được: 280 ms (2 trang), 129 ms (1 trang), 137 ms (1 trang). Chưa có ngưỡng để so. | Bị chặn | [log](../_logs/reg03-worker.log) |

## Log

- [reg03-worker.log](../_logs/reg03-worker.log)

## Ghi chú / lỗi phát hiện

- (không có)
