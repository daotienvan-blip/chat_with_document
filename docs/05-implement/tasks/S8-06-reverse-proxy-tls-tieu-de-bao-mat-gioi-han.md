# S8-06 — Reverse proxy: TLS, tiêu đề bảo mật, giới hạn tốc độ, allowlist, lỗi problem+json

| | |
|---|---|
| **Lát cắt** | S8 — Củng cố, vận hành và cổng phát hành (mốc M4) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S8-05](S8-05-dong-goi-dockerfile-compose-san-xuat-tat-em.md) |
| **Truy vết** | NFR-SEC-001, A-06, OQ-A01, CON-005 |
| **Bị chặn bởi** | OQ-A01 (nếu quyết định không dùng nginx thì làm lại theo proxy được chọn) |
| **Trạng thái** | ✅ Xong (2026-10-27) — `nginx -t` qua (proxy healthy); `make proxy-test` 13/13 |

## Mục tiêu

Biên mạng đúng như thiết kế: TLS, tệp tĩnh SPA, ghi đè `X-Request-Id`, giới hạn kích thước/tốc độ, chỉ cho mạng nội bộ, và lỗi ở tầng proxy cũng là `problem+json`.

## Đọc trước

- SAD §4.1
- API_Design §3.5.1, §3.5.3, §3.8.2
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `deploy/proxy/nginx.conf`, `error-pages/*.json`
- `make proxy-test`

## Các bước

1. TLS ≥ 1.2 (chứng chỉ mount từ ngoài); `client_max_body_size` cao hơn giới hạn tệp một chút; ghi đè `X-Request-Id`.
2. Tiêu đề: CSP `default-src 'self'`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `frame-ancestors 'none'`; không CORS.
3. `limit_req` theo địa chỉ: 30/phút cho `/api/v1/questions`, 10/phút cho `POST /api/v1/documents`, 120/phút còn lại; `limit_req_status 429`; `allow/deny` mạng nội bộ (cấu hình được).
4. `error_page` 413/429/502/504 trả thân `application/problem+json` đúng schema (giải quyết OQ-A01); `/metrics` chỉ mở cho mạng hạ tầng; gzip cho JSON.

## Tiêu chí hoàn thành

- [x] `nginx -t` thành công trong container; `make proxy-test` (curl) kiểm: tiêu đề có mặt, 413 khi tệp quá lớn, 429 sau khi vượt hạn mức, đều ở dạng `problem+json`.
- [x] Truy cập từ địa chỉ không nằm trong allowlist bị từ chối.
- [x] `curl -I` không lộ phiên bản máy chủ.
- [x] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Quản lý chứng chỉ.

## Ghi chú và rủi ro

- Hạn mức theo địa chỉ có rủi ro NAT/VPN (API_Design §3.8.2); để cấu hình theo biến môi trường.

## Kết quả chạy (2026-10-27)

`make prod-up` rồi `make proxy-test` (`deploy/proxy/proxy-test.sh`): **13/13**.

- TLS 1.2+ được nhận, TLS 1.1 bị từ chối (chứng chỉ tự ký sinh bởi `make prod-env`).
- Tiêu đề CSP `default-src 'self'; frame-ancestors 'none'`, `nosniff`, `no-referrer`; không CORS; `Server: nginx` không kèm phiên bản.
- `X-Request-Id` client gửi bị ghi đè bằng `$request_id` (32 hex).
- 413 (tệp 220 MB) và 429 (sau 7 câu hỏi liên tiếp, có `Retry-After`) đều là `application/problem+json`, đủ trường bắt buộc của schema `Problem`, `requestId` thật. 502 kiểm trong `rolling-test.sh` (S8-05).
- `/metrics` từ máy dev ⇒ 403; truy cập từ mạng `100.64.10.0/24` (ngoài allowlist) ⇒ 403.

**Thay đổi so với bản viết trước:** chạy `nginx-unprivileged` (cổng 8443, uid 101); trang lỗi trả bằng `return` trong `nginx.conf` để mang `requestId` thật (bỏ `error-pages/*.json` có `requestId` rỗng); allowlist tách ra `proxy/allowlist.conf` để mount đè; bật keepalive tới upstream (`proxy_http_version 1.1`).

**Lưu ý:** 403 từ allowlist là thân mặc định của nginx (không phải `problem+json`), vì `ProblemCode` không có mã phù hợp và người ngoài mạng không phải người dùng ứng dụng. Hạn mức theo địa chỉ vẫn có rủi ro NAT/VPN (API_Design §3.8.2).
