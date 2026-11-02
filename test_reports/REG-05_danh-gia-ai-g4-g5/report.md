# Test report – REG-05: Đánh giá AI G4, G5

| Trường | Giá trị |
|---|---|
| Test case | [REG-05](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.7, §6.12 |
| Kết luận | **ĐẠT** |
| Bắt đầu | — |
| Kết thúc | 2026-11-02T11:50:14.906Z |
| Cách thực hiện | Tự động – `make eval` (`eval_cwd.run`, AI giả trích xuất, 15 câu tổng hợp, 2 lần chạy) |
| URL ứng dụng | — |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | G5 – câu ngoài tài liệu trả `not_found` | 100% | 100% | Đạt | [log](../_logs/reg05-eval-report.md) |
| 2 | G4 – câu có trả lời mà mọi nguồn đúng tài liệu kỳ vọng | 100% | 100% | Đạt | [log](../_logs/reg05-eval-report.md) |
| 3 | Cùng câu hỏi, 2 lần chạy cùng kết quả | 100% | 100% | Đạt | [log](../_logs/reg05-eval-report.md) |
| 4 | Nguồn phủ đủ tài liệu kỳ vọng | Không có ngưỡng (theo dõi) | 100% | Đạt | [log](../_logs/reg05-eval-report.md) |
| 5 | Trang đúng khi có kỳ vọng | Không có ngưỡng (theo dõi) | 100% | Đạt | [log](../_logs/reg05-eval-report.md) |

## Log

- [reg05-eval-report.md](../_logs/reg05-eval-report.md)
- [reg05-grading.csv](../_logs/reg05-grading.csv)

## Ghi chú / lỗi phát hiện

- G3 (độ đúng nội dung) không thuộc bộ này: cần người chấm cột cuối của `reg05-grading.csv`, ngưỡng `[TBD: OQ-004]` — xem UAT-02.
- Câu `q15` (ca hồi quy của DEF-001) nay trả `not_found`: G5 lên 100% từ 80% ngày 28/10.
- Bộ `synthetic.jsonl` nhỏ và đã được dùng để chỉnh AI giả, nên kết quả có thiên lệch (test-plan §6.12).
