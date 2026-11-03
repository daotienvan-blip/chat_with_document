---
name: change-api-contract
description: Thay đổi hợp đồng API hoặc lược đồ CSDL của "Chat với tài liệu" (openapi.yaml, schema.sql, migration, client web sinh tự động). Dùng khi thêm/sửa endpoint, trường phản hồi, mã lỗi hoặc bảng/cột.
---

# Đổi hợp đồng API / lược đồ

## API (`docs/04-design/openapi.yaml`)

`openapi.yaml` là nguồn sự thật cho cả server lẫn web:

1. Sửa `docs/04-design/openapi.yaml` trước.
2. Sinh lại kiểu cho web: `cd app/web && npm run gen:api` (ghi `src/api-client/generated.ts`, **không sửa tay** tệp này).
3. Sửa route trong `app/server/cwd_server/api/app.py` (toàn bộ route nằm ở đây; `api/routers/` đang rỗng) và `api/schemas.py`.
4. Lỗi trả về dạng RFC 7807 problem+json qua `api/problems.py`; thêm mã lỗi mới vào cả `openapi.yaml` lẫn `problems.py`.
5. Cập nhật `docs/04-design/API_Design.md` nếu hành vi người dùng thấy được thay đổi.
6. Chạy `make contract` — integration test kiểm mọi phản hồi theo `openapi.yaml`, nên lệch hợp đồng sẽ đỏ.

## Lược đồ CSDL (`docs/04-design/schema.sql`)

`schema.sql` **được thực thi lúc chạy**, không chỉ là tài liệu:

- Migration `0001_init` và fixture test (`tests/conftest.py`) đều render tệp này; fixture test **không chạy Alembic**.
- Chỉ thêm migration mới thì schema test không đổi; chỉ sửa `schema.sql` thì CSDL đã migrate không đổi.
- Vì vậy khi đổi lược đồ: sửa `schema.sql` (cho test và cài mới), thêm migration Alembic trong `app/server/cwd_server/persistence/migrations/versions/` (cho CSDL đã có), và cập nhật `docs/04-design/Database_Design.md`.
- Giữ vai trò CSDL tối thiểu quyền (`deploy/prod-local/init-roles.sh`, `tests/integration/test_privileges.py`); bảng mới phải được cấp quyền đúng.

## Kiểm tra cuối

`make check` rồi `make contract`; báo rõ AC nào được chứng minh (xem skill `write-test-with-req-id`). Giá trị chưa được quyết định giữ nguyên dạng `[TBD: OQ-…]`, không tự bịa.
