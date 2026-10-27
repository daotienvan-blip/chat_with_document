# S8-02 — Vai trò CSDL tối thiểu và kiểm thử quyền

| | |
|---|---|
| **Lát cắt** | S8 — Củng cố, vận hành và cổng phát hành (mốc M4) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S6-02](S6-02-handler-purge-document-va-cuoc-dua-xu-ly-xoa.md), [S3-05](S3-05-api-post-questions.md) |
| **Truy vết** | D-06, DQ-05, NFR-SEC-001 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Test chạy bằng vai trò đăng nhập thật, 11 thao tác bị cấm bị từ chối |

## Mục tiêu

`api` và `worker` chạy bằng hai vai trò đăng nhập riêng chỉ có quyền cần thiết; có test chứng minh các thao tác bị cấm thật sự bị từ chối.

## Đọc trước

- schema.sql (GRANT)
- Database_Design §4.1, §3.5.2
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `deploy/compose.dev.yaml` (tạo vai trò đăng nhập + mật khẩu từ biến môi trường)
- `DATABASE_URL_API`, `DATABASE_URL_WORKER`, `DATABASE_URL_MIGRATE` trong cấu hình
- `server/tests/integration/test_privileges.py`

## Các bước

1. Tạo vai trò đăng nhập `cwd_api_login` (thuộc `cwd_api`) và `cwd_worker_login` (thuộc `cwd_worker`); migration chạy bằng vai trò chủ sở hữu.
2. Đặt `statement_timeout` bằng `ALTER ROLE <đăng nhập> SET …` (30 s cho api; dài hơn cho worker) — cài đặt theo vai trò không kế thừa qua vai trò nhóm.
3. Chạy lại toàn bộ bộ test tích hợp với đúng vai trò (api dùng cho các router, worker cho handler) để lộ mọi quyền còn thiếu.
4. Test quyền: api **không** thể INSERT/UPDATE/DELETE `chunks`, DELETE `documents`, UPDATE cột khác `deleted_at`; worker **không** thể UPDATE `deleted_at` hay `name`.

## Tiêu chí hoàn thành

- [ ] `make test-int` xanh khi `api` và `worker` dùng vai trò thật.
- [ ] `test_privileges.py` có ≥ 8 khẳng định “bị từ chối” cụ thể.
- [ ] `SELECT … FOR UPDATE` trên `documents` của worker hoạt động (quyền UPDATE theo cột đủ).
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Mã hóa lưu trữ/TLS tới CSDL (S8-06, S8-05).
