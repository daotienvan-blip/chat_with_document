# S1-03 — API tài liệu: POST /documents, GET /documents, GET /documents/{id}

| | |
|---|---|
| **Lát cắt** | S1 — Tải PDF lên và xem danh sách (UC07, UC08, UC11) (mốc M1) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S1-02](S1-02-documentrepository-jobrepository-enqueue-va.md) |
| **Truy vết** | UC07, UC11, US-001-AC1, US-001-AC2, US-001-AC3, US-004-AC1, BR-003 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Kiểm tra tệp, tải lên nguyên tử + bù trừ, API, danh sách + polling, tải lên có tiến độ/hủy/thử lại |

## Mục tiêu

Ba endpoint hoạt động đúng `openapi.yaml`, kể cả mã lỗi, `Location` và hình dạng JSON.

## Đọc trước

- openapi.yaml (uploadDocument, listDocuments, getDocument)
- API_Design §3.5.2 mục 2–4
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/cwd_server/api/routers/documents.py`, `schemas.py`
- `server/tests/api/test_documents_api.py`
- `server/tests/support/openapi_assert.py` (hàm kiểm tra phản hồi theo OpenAPI, dùng lại ở S8-03)

## Các bước

1. `POST /api/v1/documents` (multipart, một phần `file`): kiểm tra `Content-Length` sớm (vượt → `413`), gọi `validate_upload` rồi `DocumentService.upload`; trả `202` + body `Document` + `Location`.
2. `GET /documents` → `{items,total}`; `GET /documents/{id}` → `Document` hoặc `404 NOT_FOUND`. Chỉ trường có trong schema; không lộ `storage_key`, `content_sha256`, `deleted_at`.
3. Viết `assert_matches_openapi(response, path, method)` (dùng `openapi-core` hoặc jsonschema trích từ `openapi.yaml`) và gọi trong mọi test của router.
4. Lỗi: `UNSUPPORTED_TYPE` 400, `FILE_TOO_LARGE` 413 kèm `limit`, `INVALID_REQUEST` khi không có phần `file`, `STORAGE_UNAVAILABLE` 503.

## Tiêu chí hoàn thành

- [ ] `make check` và `make test-int` xanh; mọi phản hồi trong test qua `assert_matches_openapi`.
- [ ] Test: US-001-AC2, US-001-AC3, US-004-AC1 (liệt kê đủ tài liệu, đúng thứ tự, kèm trạng thái).
- [ ] Test: tải lên thành công → `GET /documents` ngay sau đó thấy tài liệu `processing` (đọc-sau-ghi).
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- `DELETE` (S6-01), `GET …/file` (S4-02).
- Giới hạn tốc độ (S7-01).

## Ghi chú và rủi ro

- Starlette đã nhận hết thân multipart trước khi vào hàm; giới hạn cứng thật phải đặt ở proxy (S8-06). Ghi chú điều này vào docstring.
