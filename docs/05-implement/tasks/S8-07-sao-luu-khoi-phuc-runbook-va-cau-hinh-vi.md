# S8-07 — Sao lưu/khôi phục, runbook và cấu hình vị trí lưu trữ (US-015)

| | |
|---|---|
| **Lát cắt** | S8 — Củng cố, vận hành và cổng phát hành (mốc M4) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S8-05](S8-05-dong-goi-dockerfile-compose-san-xuat-tat-em.md), [S8-02](S8-02-vai-tro-csdl-toi-thieu-va-kiem-thu-quyen.md) |
| **Truy vết** | US-015-AC1, BR-016, G8, G11, DQ-04, DQ-07, NFR-SEC-002 |
| **Bị chặn bởi** | OQ-005, OQ-D01 |
| **Trạng thái** | ✅ Xong (2026-10-27) — Sao lưu/khôi phục đã chạy thử; runbook; `DATA_LOCATION.md` (chữ ký trống, chờ OQ-005) |

## Mục tiêu

Có quy trình sao lưu/khôi phục đã chạy thử và tài liệu để CNTT phê duyệt vị trí lưu trữ.

## Đọc trước

- Database_Design §5.2, §5.3, §5.5
- SAD §4.1 (Vị trí dữ liệu)
- PRD G8, G11
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `deploy/{backup.sh,restore.sh}`
- `docs/05-implement/runbook.md`
- `deploy/DATA_LOCATION.md`

## Các bước

1. `backup.sh`: `pg_dump -Fc` giữ 7 bản; hướng dẫn bật versioning bucket. `restore.sh`: dựng CSDL từ bản dump rồi chạy `reconcile()` (S7-04).
2. Chạy thử khôi phục trên compose: dump → xóa CSDL → khôi phục → `GET /documents` khớp kho (ghi kết quả vào runbook; DQ-07).
3. Runbook: khởi động/dừng, migrate, xoay vòng bí mật, **xử lý sự cố xóa khẩn cấp** (xóa tài liệu ngay; dữ liệu còn trong bản sao lưu tới 7 ngày — OQ-D01), quy trình đổi mô hình embedding (Database_Design §5.3), đọc cảnh báo.
4. `DATA_LOCATION.md`: bảng liệt kê chính xác nơi lưu CSDL, kho tệp, nhật ký, nhà cung cấp AI và vùng địa lý, kèm ô phê duyệt của CNTT/pháp lý (G8, AC-016).

## Tiêu chí hoàn thành

- [ ] Biên bản khôi phục thử thành công có ngày giờ trong runbook.
- [ ] `DATA_LOCATION.md` điền được bằng cấu hình thật của môi trường thử; ô chữ ký để trống chờ phê duyệt.
- [ ] Runbook được một người khác đọc và chạy theo được các bước cốt lõi (ghi lại trong PR).
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- PITR/WAL (không dùng ở MVP).

## Ghi chú và rủi ro

- US-015 là story của đại diện CNTT: bằng chứng là tài liệu cấu hình + chữ ký, không phải màn hình.
