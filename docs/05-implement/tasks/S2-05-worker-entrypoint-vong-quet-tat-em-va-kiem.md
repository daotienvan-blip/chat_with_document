# S2-05 — Worker: entrypoint, vòng quét, tắt êm và kiểm thử đầu-cuối tải lên → ready

| | |
|---|---|
| **Lát cắt** | S2 — Xử lý tài liệu đến khi sẵn sàng hoặc lỗi (UC09, UC10) (mốc M1) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S2-04](S2-04-ingestionservice-process-tu-pdf-den-doan-co.md), [S1-03](S1-03-api-tai-lieu-post-documents-get-documents.md) |
| **Truy vết** | UC09, NFR-PRF-002, QAS-03 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | 🟡 Một phần (2026-10-27) — Worker, vòng quét, SIGTERM dừng êm. Chưa có test tự động cho kill -9 giữa chừng (chỉ test `release_overdue`) |

## Mục tiêu

Chạy được `worker` như tiến trình riêng; một PDF thật đi từ `POST /documents` đến `ready` trong môi trường compose.

## Đọc trước

- SAD §2.2.3, §5.1
- Blueprint §3.8.2
- Database_Design §5.5
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/cwd_server/worker/{__main__,sweeper}.py`
- `deploy/compose.dev.yaml` (dịch vụ `worker`)
- `server/tests/integration/test_upload_to_ready.py`

## Các bước

1. `python -m cwd_server.worker`: dựng container, chạy `Runner`; SIGTERM → hoàn tất việc hiện tại (tối đa 45 s) rồi thoát.
2. Vòng quét mỗi 5 phút: `release_overdue`, `cleanup` việc cũ.
3. Test E2E mức dịch vụ: khởi động app thật + `Runner.run_once()` trong cùng tiến trình, `FakeLlm`, MinIO/PostgreSQL thật; tải một PDF fixture, chạy runner, `GET /documents` thấy `ready`.
4. Ghi log thời gian xử lý mỗi tài liệu (bằng chứng cho NFR-PRF-002).

## Tiêu chí hoàn thành

- [ ] `make test-int` xanh phần E2E.
- [ ] `make up` khởi động được `worker`; gửi SIGTERM khi đang xử lý → tiến trình thoát mã 0 sau khi xong việc.
- [ ] Kill -9 worker khi đang xử lý rồi khởi động lại → tài liệu cuối cùng `ready`, không đoạn trùng (QAS-03).
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Đóng gói ảnh container sản xuất (S8-05).

## Ghi chú và rủi ro

- Mốc M1 (phía backend) đạt sau task này.
