# S0-04 — CSDL: migration 0001, phiên làm việc và kiểm thử ràng buộc

| | |
|---|---|
| **Lát cắt** | S0 — Khung chạy được (walking skeleton) (mốc M0) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S0-02](S0-02-moi-truong-dev-bang-docker-compose.md), [S0-03](S0-03-nen-tang-server-cau-hinh-log-loi-problem.md) |
| **Truy vết** | BR-001, BR-004 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Alembic 0001 thực thi `schema.sql`; test từng ràng buộc |

## Mục tiêu

Áp dụng được lược đồ `schema.sql` lên PostgreSQL thật bằng Alembic, có lớp truy cập SQLAlchemy và bộ test chứng minh từng ràng buộc CHECK/UNIQUE/FK hoạt động.

## Đọc trước

- schema.sql
- Database_Design §3.2, §5.3
- Blueprint §3.4.1
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/alembic.ini`, `server/cwd_server/persistence/migrations/versions/0001_init.py`
- `server/cwd_server/persistence/{db,models}.py`
- `server/tests/integration/test_schema_constraints.py`

## Các bước

1. Alembic `0001_init`: thực thi nội dung `docs/04-design/schema.sql` (đọc từ tệp, không chép tay). Cho phép đặt số chiều qua biến `EMBEDDING_DIM` bằng cách thay `vector(1536)` trước khi chạy `[TBD: OQ-S01]`.
2. `db.py`: engine, `sessionmaker`, quản lý giao dịch (`with session.begin()`), hồ bơi kết nối cấu hình được.
3. `models.py`: ORM/Core cho `documents`, `chunks`, `jobs` đúng cột. Một test đối chiếu mô hình với CSDL thật (reflection) để không lệch.
4. Test tích hợp: với từng ràng buộc trong Database_Design §3.2 (“Bất biến do CSDL bảo đảm”) viết một INSERT vi phạm và kiểm tra bị từ chối; một INSERT hợp lệ được chấp nhận; `ON DELETE CASCADE` xóa đoạn; `jobs_active_uq` chặn việc trùng đang hoạt động.
5. `make migrate` chạy `alembic upgrade head`; `alembic downgrade base` dọn sạch.

## Tiêu chí hoàn thành

- [ ] `make up && make migrate && make test-int` xanh.
- [ ] Test ràng buộc phủ đủ: `failed_iff_reason`, `ready_iff_time`, `key_format`, `pages_ok`, `doc_index_uq`, `running_locked`, `jobs_active_uq`.
- [ ] Chạy `upgrade` rồi `downgrade` rồi `upgrade` không lỗi.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Chưa có repository (S1-02, S2-03, S3-01).
- Chưa phân quyền vai trò (S8-02).

## Ghi chú và rủi ro

- Không đổi `schema.sql` trong task này; nếu phát hiện lỗi lược đồ, sửa `schema.sql` và `Database_Design.md` cùng lúc (PLAN §2.3).
