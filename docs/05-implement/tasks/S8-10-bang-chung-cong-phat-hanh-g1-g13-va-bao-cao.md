# S8-10 — Bằng chứng cổng phát hành G1–G13 và báo cáo phủ yêu cầu

| | |
|---|---|
| **Lát cắt** | S8 — Củng cố, vận hành và cổng phát hành (mốc M4) |
| **Cỡ** | S (1–3 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S8-03](S8-03-bo-kiem-thu-hop-dong-theo-openapi-yaml.md), [S8-04](S8-04-bo-danh-gia-chat-luong-ai-eval-tap-cau-hoi.md), [S8-07](S8-07-sao-luu-khoi-phuc-runbook-va-cau-hinh-vi.md), [S8-08](S8-08-kiem-thu-e2e-playwright-va-kiem-tra-tiep.md) |
| **Truy vết** | G1, G2, G3, G4, G5, G8, G9, G11, G12, G13 |
| **Bị chặn bởi** | OQ-004 (G3), OQ-005 (G8) |
| **Trạng thái** | ✅ Xong (2026-10-27) — `release-gates.md`, `make trace` |

## Mục tiêu

Một tài liệu duy nhất cho biết mỗi cổng phát hành có bằng chứng nào, ở đâu, trạng thái gì; và một script báo cáo AC chưa có test.

## Đọc trước

- PRD §5.1
- docs/03-analysis/traceability.md
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `docs/05-implement/release-gates.md`
- `server/scripts/trace_check.py`
- `make trace`

## Các bước

1. Bảng G1–G13: tiêu chí, lệnh/tài liệu làm bằng chứng, trạng thái (Đạt / Chưa / Chặn bởi OQ-xxx), người chịu trách nhiệm (`[TBD: OQ-007]`).
2. `trace_check.py`: thu thập marker `req(...)` của pytest và mã `[US-xxx-ACn]` trong tên test web; in AC của USER_STORIES.md chưa có test.
3. Đối chiếu `docs/03-analysis/traceability.md`: ghi vào đầu `release-gates.md` các thay đổi so với kế hoạch (nếu có).

## Tiêu chí hoàn thành

- [ ] `make trace` chạy và in danh sách AC chưa phủ (mục tiêu: rỗng ngoại trừ AC chặn bởi OQ, có ghi chú).
- [ ] `release-gates.md` có đủ 10 cổng của PRD (G1–G5, G8, G9, G11–G13) với trạng thái trung thực.
- [ ] Không đánh dấu “Đạt” cho G3/G8 khi OQ-004/OQ-005 chưa đóng.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- (không có điều gì đặc biệt; không mở rộng sang việc của task khác)

## Ghi chú và rủi ro

- G3 và G8 chỉ có thể đạt sau quyết định của business owner và CNTT/pháp lý.
