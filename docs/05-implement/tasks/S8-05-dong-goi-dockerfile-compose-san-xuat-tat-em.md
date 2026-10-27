# S8-05 — Đóng gói: Dockerfile, compose sản xuất, tắt êm và migration

| | |
|---|---|
| **Lát cắt** | S8 — Củng cố, vận hành và cổng phát hành (mốc M4) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S8-02](S8-02-vai-tro-csdl-toi-thieu-va-kiem-thu-quyen.md), [S7-01](S7-01-loadguard-va-gioi-han-toc-do-o-ung-dung.md) |
| **Truy vết** | QAS-08, C-11 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — `make prod-up` trên Colima: 2 api + worker + proxy healthy, smoke 17/17 qua HTTPS; nâng cấp cuốn chiếu 7/7 (`deploy/prod-local/rolling-test.sh`) |

## Mục tiêu

Dựng được `api`, `worker`, `web` thành ảnh container chạy bằng compose kiểu sản xuất.

## Đọc trước

- SAD §5.1, §5.2
- Blueprint §3.8.2
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `deploy/{Dockerfile.server,Dockerfile.web,compose.prod.yaml}`
- `deploy/env.prod.example`

## Các bước

1. Ảnh nhiều tầng, người dùng không đặc quyền; `worker` hệ tệp chỉ-đọc (thư mục tạm riêng) và không có đường ra mạng ngoài PostgreSQL, kho, IF-02 (mô tả bằng mạng compose).
2. Dịch vụ `migrate` chạy một lần trước `api`/`worker` (không tự migrate khi `api` khởi động).
3. `uvicorn --timeout-graceful-shutdown 45`; `api` ≥ 2 bản; healthcheck dùng `/healthz`, `/readyz`; giới hạn tài nguyên theo SAD §5.2.
4. Bí mật qua biến môi trường/secret của compose; không có trong ảnh hay log.

## Tiêu chí hoàn thành

- [x] `docker compose -f deploy/compose.prod.yaml up -d` xong, `readyz` trả 200.
- [x] Nâng cấp cuốn chiếu thử: dừng một bản `api` khi có yêu cầu đang chạy ⇒ yêu cầu hoàn tất (ghi lại cách thử).
- [x] Quét ảnh không chạy bằng root; `docker inspect` cho thấy người dùng khác root.
- [x] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Proxy/TLS (S8-06).

## Kết quả chạy (2026-10-27)

Lệnh (trong `app/`): `make prod-up` → `deploy/prod-local/rolling-test.sh <id PDF lớn>` → `make prod-down`.
`compose.prod.local.yaml` thêm PostgreSQL + S3 (SeaweedFS) giả lập hạ tầng; bí mật sinh ngẫu nhiên vào `app/var/prod-local/` (không commit).

- `readyz` 200 qua proxy; `smoke.py` 17/17 qua `https://localhost:8443` với api chạy bằng `cwd_api_login`, worker bằng `cwd_worker_login`, kho S3.
- Nâng cấp cuốn chiếu 7/7:
  - Qua proxy: `docker stop` một bản api giữa lúc tải 23 MB ⇒ tải xong đúng sha256; 10/10 yêu cầu mới vẫn 200. Ghi chú: nginx đệm phản hồi nên api thường đã giao xong cho proxy.
  - Gọi thẳng api bằng client đọc chậm, SIGTERM giữa chừng ⇒ uvicorn chờ 10 s cho yêu cầu xong, thoát mã 0, client nhận đủ byte.
  - Dừng cả hai bản ⇒ proxy trả 502 `problem+json`; khởi động lại ⇒ `readyz` 200.
- Không root: `cwd-server` uid 10001, `cwd-proxy` uid 101 (nginx-unprivileged). Mọi container `read_only` + `no-new-privileges`.
- Bí mật: 0 lần xuất hiện trong `docker history`, env của image, log mọi container.
- Worker: chỉ mạng `data` (internal) — không ra được Internet, không thấy proxy; hệ tệp chỉ-đọc; `docker stop` thoát mã 0.
- `make check` xanh; `make test-int` 29/29.

**Lỗi tìm thấy và đã sửa**
- `/readyz` đọc bảng `jobs` ⇒ với vai trò `cwd_api` (chỉ có INSERT trên `jobs`) luôn trả 503, api không bao giờ healthy. Sửa: kiểm `has_table_privilege('jobs','INSERT')`; thêm `test_readyz_queries_work_under_least_privilege`.
- `Dockerfile.server` dùng đường dẫn `server/…` trong khi context là gốc dự án ⇒ không build được. Sửa đường dẫn, thêm `.dockerignore` ở gốc dự án (dạng whitelist).

**Chưa kiểm chứng:** hạ tầng thật (PostgreSQL/S3 được quản lý, bộ quản lý bí mật); `deploy.resources.limits` chỉ áp dụng trong giới hạn của máy ảo Colima (3 GB); đường ra có kiểm soát cho AI thật (IF-02) khi `LLM_PROVIDER=http`.
