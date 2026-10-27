# S2-03 — Hàng đợi việc nền: claim/complete/fail/sweep và backoff

| | |
|---|---|
| **Lát cắt** | S2 — Xử lý tài liệu đến khi sẵn sàng hoặc lỗi (UC09, UC10) (mốc M1) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Server / hạ tầng |
| **Phụ thuộc** | [S0-04](S0-04-csdl-migration-0001-phien-lam-viec-va-kiem.md), [S1-02](S1-02-documentrepository-jobrepository-enqueue-va.md) |
| **Truy vết** | UC09, QAS-03, D-05 |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ✅ Xong (2026-10-27) — Chunker, hàng đợi (đồng thời, backoff, hoàn lần thử), xử lý tài liệu (idempotent, xóa giữa chừng) |

## Mục tiêu

Bảng `jobs` hoạt động như hàng đợi an toàn nhiều worker: nhận việc không trùng, thử lại có lịch, phục hồi việc bị bỏ rơi.

## Đọc trước

- Blueprint §3.4.3 (truy vấn 3–5), §3.7.2
- Database_Design §5.1 (T2)
- SAD §2.2.3
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `server/cwd_server/persistence/repositories.py` (mở rộng `JobRepository` đã có `enqueue` từ S1-02)
- `server/cwd_server/worker/runner.py`, `backoff.py`
- `server/tests/integration/test_job_queue.py`

## Các bước

1. `claim()` bằng đúng câu `UPDATE … FOR UPDATE SKIP LOCKED … RETURNING` (khóa 10 phút); `complete(id)` (đặt `done`, `finished_at`); `fail(id, error, run_after, count_attempt)` (nếu `count_attempt=false` hoàn lại `attempts`); `release_overdue()`; `cleanup(older_than=7 ngày)`.
2. `next_run_after(attempts)`: lần 1 → +30 s, lần 2 → +2 phút, lần 3 → kết thúc (`failed`).
3. `Runner(handlers, poll_interval, stop_event)`: lặp nhận việc, gọi handler theo `type`; phân biệt lỗi thử lại được (xếp lại) và lỗi kết thúc.
4. Test đồng thời: nhiều luồng `claim()` trên N việc, mỗi việc chỉ được nhận một lần.

## Tiêu chí hoàn thành

- [ ] `make test-int` xanh với các test: đồng thời, quá hạn khóa được trả về hàng đợi, backoff đúng, `count_attempt=false` không tăng `attempts`, `jobs_active_uq` chặn enqueue trùng.
- [ ] Không có `sleep` thật dài trong test (đồng hồ có thể tiêm).
- [ ] `make check` xanh.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- Handler thật (S2-04, S6-02).
- Entry point tiến trình (S2-05).

## Ghi chú và rủi ro

- Giữ giao dịch ngắn; không giữ khóa dòng trong khi gọi dịch vụ ngoài.
