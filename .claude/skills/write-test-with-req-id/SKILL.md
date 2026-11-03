---
name: write-test-with-req-id
description: Viết hoặc sửa test cho repo "Chat với tài liệu" theo quy ước truy vết yêu cầu (gắn mã US-xxx-ACn). Dùng khi thêm tính năng, sửa lỗi cần ca hồi quy, hoặc khi `make trace` báo AC chưa có test.
---

# Viết test có mã yêu cầu

Mỗi test chứng minh một tiêu chí chấp nhận (AC) trong `docs/03-analysis/USER_STORIES.md` phải mang mã AC đó. `make trace` (script `app/server/scripts/trace_check.py`) đối chiếu và thoát lỗi nếu còn AC chưa có test.

## Cách gắn mã

Server (pytest) — dùng marker `req`, có thể xếp nhiều marker:

```python
@pytest.mark.req("US-001-AC2")
@pytest.mark.req("US-001-AC3")
def test_upload_rejects_non_pdf(...): ...
```

Web (vitest) — đặt mã trong ngoặc vuông ở đầu tên test:

```ts
it("[US-001-AC3] tệp không phải PDF bị từ chối, không gửi yêu cầu tải lên", async () => { ... });
```

## Chọn tầng test

- Logic thuần ở `core/` → `tests/unit/` với adapter giả; dựng container bằng `build_container(..., llm=, store=, extractor=)`.
- Hành vi qua DB, hàng đợi, API → `tests/integration/` (cần PostgreSQL, xem skill `run-checks`). Phản hồi API phải được kiểm theo `openapi.yaml` qua `tests/support/openapi_assert.py`.
- PDF mẫu: dùng `tests/fixtures/pdfs.py`, không commit PDF nhị phân.
- Giao diện → `app/web/src/**/*.test.tsx`.

## Quy tắc

1. Sửa lỗi: viết test tái hiện lỗi trước, thấy đỏ, rồi mới sửa. Ghi lỗi và ca hồi quy vào `docs/07-verification/review-record.md` / `docs/05-implement/release-gates.md` trong cùng PR.
2. Không đổi mã AC của test cũ cho khớp; nếu AC đổi thì sửa `USER_STORIES.md` có chủ đích.
3. Log và thông báo lỗi trong test không được chứa nội dung tài liệu hay câu hỏi (chính sách log của dự án).
4. Tên test, chú thích, chuỗi hiển thị bằng tiếng Việt như phần còn lại của repo.
5. Chạy `make trace` sau khi thêm test và báo kết quả `x/y AC có test`.
