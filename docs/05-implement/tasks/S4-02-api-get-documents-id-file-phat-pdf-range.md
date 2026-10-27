# S4-02 — API GET /documents/{id}/file: phát PDF, Range, ETag

| | |
|---|---|
| **Lát cắt** | S4 — Số trang và mở tài liệu nguồn (UC16, UC17) (mốc M2) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S1-03](S1-03-api-tai-lieu-post-documents-get-documents.md), [S0-06](S0-06-adapter-object-storage-s3-va-quy-tac-phu.md) |
| **Truy vết** | UC17, US-008-AC1, BR-008 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Range/206/416/304/ETag. Chưa đo bộ nhớ với tệp 100 MB |

## Mục tiêu

Trình xem PDF của trình duyệt mở được tài liệu nguồn, hỗ trợ tải từng phần, và tài liệu đã xóa trả `404`.

## Đọc trước

- openapi.yaml (getDocumentFile)
- API_Design §3.4.3, §3.5.2 mục 6
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/cwd_server/api/routers/files.py`
- `ObjectStorePort`/adapter hỗ trợ range
- `server/tests/api/test_file_api.py`

## Các bước

1. Truy xuất tài liệu `deleted_at IS NULL` (kể cả `processing/failed`); không có ⇒ `404 NOT_FOUND`.
2. Phát luồng từ kho, không đọc cả tệp vào bộ nhớ; `Content-Type: application/pdf`, `Content-Disposition: inline; filename*=UTF-8''…`, `X-Content-Type-Options: nosniff`, `Accept-Ranges: bytes`, `ETag: "<sha256>"`, `Cache-Control: private, max-age=0, must-revalidate`.
3. `Range` ⇒ `206` + `Content-Range`; sai ⇒ `416`; `If-None-Match` khớp ⇒ `304` `[Đề xuất]`.
4. Kho lỗi ⇒ `503 STORAGE_UNAVAILABLE`.

## Tiêu chí hoàn thành

- [ ] `make test-int` xanh: tải toàn bộ khớp byte với tệp đã tải lên; các biến thể `Range` (đầu, giữa, hậu tố, sai); đã xóa mềm ⇒ `404`; tên tệp tiếng Việt trong header đúng.
- [ ] Mọi phản hồi qua `assert_matches_openapi` (phần header).
- [ ] Đo bộ nhớ khi tải tệp 100 MB giả lập: không tăng theo kích thước.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Trang HTML cho 404 khi điều hướng (S8-09, OQ-A02).
