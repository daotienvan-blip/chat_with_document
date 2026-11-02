# Test report – REG-04: Proxy và nâng cấp cuốn chiếu

| Trường | Giá trị |
|---|---|
| Test case | [REG-04](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.7 |
| Kết luận | **KHÔNG ĐẠT** |
| Bắt đầu | 2026-11-02T11:52:59.747Z |
| Kết thúc | 2026-11-02T12:02:17.675Z (557.9 s) |
| Cách thực hiện | Tự động – `deploy/proxy/proxy-test.sh` và `deploy/prod-local/rolling-test.sh` trên stack `make prod-up` |
| URL ứng dụng | https://localhost:8443 (stack prod cục bộ: api×2, worker, nginx TLS; ảnh build từ commit này) |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | Proxy: TLS 1.2+ được chấp nhận | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 2 | Proxy: TLS 1.1 bị từ chối | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 3 | Proxy: CSP default-src 'self'; frame-ancestors 'none' | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 4 | Proxy: X-Content-Type-Options: nosniff | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 5 | Proxy: Referrer-Policy: no-referrer | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 6 | Proxy: Server không lộ phiên bản (Server: nginx) | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 7 | Proxy: không có CORS | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 8 | Proxy: X-Request-Id bị ghi đè (nhận: 1f896737a85939b791c5ee48c18df9bf) | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 9 | Proxy: 413 → problem+json FILE_TOO_LARGE có requestId | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 10 | Proxy: câu hỏi 100 KB → proxy trả 400 QUESTION_TOO_LONG problem+json | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 11 | Proxy: câu hỏi 5.000 ký tự → api trả QUESTION_TOO_LONG, limit 4000 | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 12 | Proxy: 429 sau 6 yêu cầu → problem+json RATE_LIMITED, có Retry-After | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 13 | Proxy: thân 413/429/400 là JSON hợp lệ đủ trường bắt buộc | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 14 | Proxy: /metrics từ máy dev → 403 | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 15 | Proxy: truy cập từ 100.64.10.0/24 (ngoài allowlist) → 403 (nhận: 403) | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-proxy-test.log) |
| 16 | Cuốn chiếu: trong lúc api-1 tắt: yêu cầu mới thành công 10/10 | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-rolling-test.log) |
| 17 | Cuốn chiếu: yêu cầu đang chạy hoàn tất: HTTP 200, đúng sha256 | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-rolling-test.log) |
| 18 | Cuốn chiếu: api-1 thoát mã 0 | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-rolling-test.log) |
| 19 | Cuốn chiếu: yêu cầu đang chạy hoàn tất khi api-2 nhận SIGTERM | HTTP 200, đủ byte, đúng sha256 | Client đọc chậm không nhận đủ phản hồi và không nhận được FIN: socket vẫn ESTABLISHED tới api-2 sau hơn 5 phút dù api-2 đã thoát mã 0. Agent phải dừng client; vì vậy log ghi 0 byte. | Không đạt | [log](../_logs/reg04-rolling-test.log) [log](../_logs/reg04-rolling-b-chan-doan.txt) |
| 20 | Cuốn chiếu: api-2 chờ yêu cầu xong mới thoát (≥ 2 s) và thoát mã 0 | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-rolling-test.log) |
| 21 | Cuốn chiếu: proxy trả 502 problem+json có requestId | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-rolling-test.log) |
| 22 | Cuốn chiếu: khởi động lại: readyz 200 qua proxy | Kiểm tra đạt | ✓ | Đạt | [log](../_logs/reg04-rolling-test.log) |

## Log

- [reg04-prod-up.log](../_logs/reg04-prod-up.log)
- [reg04-proxy-test.log](../_logs/reg04-proxy-test.log)
- [reg04-rolling-test.log](../_logs/reg04-rolling-test.log)
- [reg04-rolling-b-chan-doan.txt](../_logs/reg04-rolling-b-chan-doan.txt)

## Ghi chú / lỗi phát hiện

- **Lỗi mới DEF-004** (phần B của kiểm thử cuốn chiếu): xem README, mục Lỗi phát hiện.
- Tệp mẫu cho kiểm thử cuốn chiếu là PDF 21 MB do agent sinh (7 trang, ảnh nhiễu để không nén được), tải lên rồi xóa sau khi chạy.
- Kết quả lần trước (27/10) là 7/7. Lần này là lần chạy duy nhất, chưa biết lỗi có tái hiện ổn định không.
