# S6-01 — Xóa mềm: DocumentService.delete, API DELETE và hồi quy “xóa là hết”

| | |
|---|---|
| **Lát cắt** | S6 — Xóa tài liệu (UC12) (mốc M3) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S1-03](S1-03-api-tai-lieu-post-documents-get-documents.md), [S3-03](S3-03-answerservice-g-l1-goi-llm-g-l2-dung-nguon.md) |
| **Truy vết** | UC12, US-005-AC1, US-005-AC2, BR-004, AC-004, QAS-11 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Xóa mềm, purge đúng thứ tự, race, hộp thoại tiếp cận |

## Mục tiêu

`DELETE` có hiệu lực ngay trong danh sách, truy xuất, tải tệp và hỏi đáp; việc xóa vật lý được xếp lịch.

## Đọc trước

- openapi.yaml (deleteDocument)
- API_Design §3.5.2 mục 5, §3.7.1
- Database_Design §5.1 (T4)
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `core/documents/service.py` (`delete`)
- `persistence/repositories.py` (`mark_deleted`)
- `api/routers/documents.py` (DELETE)
- `server/tests/integration/test_delete_regression.py`

## Các bước

1. Một giao dịch: `UPDATE documents SET deleted_at=now() WHERE id=:id AND deleted_at IS NULL`; `INSERT jobs(purge_document, run_after = now()+PURGE_DELAY) ON CONFLICT DO NOTHING` (`PURGE_DELAY` mặc định 1 giờ `[Đề xuất]`).
2. Ngữ nghĩa: lần đầu `204`; xóa lại khi còn xóa mềm `204`; `id` không tồn tại (kể cả đã purge) `404`.
3. Bộ hồi quy AC-004: tài liệu `ready` có đoạn; xóa; rồi `GET /documents`, `GET /documents/{id}`, `GET …/file` ⇒ không thấy / `404`; `POST /questions` không có đoạn hay tên của nó (US-005-AC2) — gồm cả trường hợp tên tài liệu nằm trong `answer` do LLM giả kịch bản (không được lọt vào `sources`).

## Tiêu chí hoàn thành

- [ ] `make test-int` xanh; test gắn `req` US-005-AC1, US-005-AC2.
- [ ] Test: gọi `DELETE` hai lần ⇒ cả hai `204` và chỉ một việc purge.
- [ ] Mọi phản hồi qua `assert_matches_openapi`.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Xử lý purge (S6-02).
- Giao diện (S6-03).
