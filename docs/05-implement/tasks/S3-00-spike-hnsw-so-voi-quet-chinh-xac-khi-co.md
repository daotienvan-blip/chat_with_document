# S3-00 — Spike: HNSW so với quét chính xác khi có điều kiện lọc

| | |
|---|---|
| **Lát cắt** | S3 — Hỏi đáp có nguồn: có căn cứ hoặc không tìm thấy (UC14, UC15, UC19, UC21) (mốc M2) |
| **Cỡ** | S (1–3 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S0-04](S0-04-csdl-migration-0001-phien-lam-viec-va-kiem.md) |
| **Truy vết** | D-04, QAS-11 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — `notes/spike-hnsw.md` |

## Mục tiêu

Quyết định bằng số liệu: dùng chỉ mục HNSW hay quét chính xác cho truy xuất vector khi phần lớn đoạn bị lọc (đang xử lý / đã xóa mềm).

## Đọc trước

- Database_Design §3.4.5, §3.5.2
- Blueprint §3.4.5
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/scripts/spike_hnsw.py`
- `docs/05-implement/notes/spike-hnsw.md` (kết quả)
- cấu hình `RETRIEVAL_MODE=exact|hnsw`, `HNSW_EF_SEARCH`

## Các bước

1. Nạp ≈ 40.000 đoạn ngẫu nhiên (đúng số chiều cấu hình) vào 200 tài liệu, trong đó ~10% xóa mềm và ~10% chưa `ready`.
2. Với 200 truy vấn, so top-20 của quét chính xác với HNSW ở `ef_search` 40/100/200 (và quét lặp nếu phiên bản pgvector hỗ trợ): recall, số dòng trả về thực tế, p50/p95 độ trễ.
3. Ghi bảng số liệu và **quyết định** vào `spike-hnsw.md`; đặt giá trị mặc định cho cấu hình. Nếu chọn quét chính xác, nêu rõ có bỏ chỉ mục HNSW bằng migration 0002 hay không.

## Tiêu chí hoàn thành

- [ ] `spike-hnsw.md` có bảng số liệu, phiên bản PostgreSQL/pgvector đã dùng, quyết định và lý do.
- [ ] Cấu hình mặc định khớp quyết định; `make check` xanh.
- [ ] Mục tiêu tham chiếu (không bắt buộc): p95 ≤ 100 ms ở 40.000 đoạn (DQ-03).
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Triển khai Retrieval (S3-01).

## Ghi chú và rủi ro

- Số liệu sinh bằng vector ngẫu nhiên chỉ đo độ trễ/số dòng trả về, không đo chất lượng ngữ nghĩa; nói rõ giới hạn này trong báo cáo.
