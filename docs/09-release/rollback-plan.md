# Kế hoạch rollback — v0.1.0

> Người quyết định rollback: release owner hoặc người trực `[TBD: OQ-007]`. Agent không thực hiện rollback trên production.

## 1. Khi nào rollback

Rollback ngay, không chờ điều tra, khi gặp một trong các tình huống:
- Một chỉ số "đỏ" ở `docs/10-operations/dashboards.md` §2 kéo dài ≥ 10 phút sau deploy.
- `make smoke` thất bại trên môi trường đích.
- Có câu trả lời chứa nội dung không có trong tài liệu, hoặc lộ nội dung tài liệu ra log hay người ngoài allowlist.

## 2. Các tầng rollback (làm từ trên xuống, dừng ở tầng đầu tiên giải quyết được)

| Tầng | Việc | Thời gian ước tính | Mất dữ liệu? |
|---|---|---|---|
| A. Công tắc | `LLM_PROVIDER=extractive` (cắt dữ liệu gửi ra AI ngoài), khởi động lại cuốn chiếu từng bản api | ~2 phút | Không |
| B. Chặn truy cập | Thu hẹp `allowlist.conf` về nhóm dự án, `nginx -s reload` | ~1 phút | Không |
| C. Ảnh trước | Redeploy **digest** ảnh của bản trước, cuốn chiếu (`docker stop -t 50` từng bản api, như `runbook.md`); worker sau cùng | ~5 phút | Không |
| D. Khôi phục CSDL | `deploy/restore.sh <bản sao lưu trước deploy> cwd` rồi đối soát | ~10 phút + kích thước dữ liệu | **Có** — mất tài liệu/câu hỏi sau thời điểm sao lưu |

## 3. Tương thích lược đồ

- Bản v0.1.0 chỉ có migration `0001`. Rollback từ bản sau về v0.1.0 chỉ an toàn nếu bản sau chỉ thêm (cột null được, bảng mới). **Mọi migration xóa/đổi cột phải tách thành 2 lần phát hành** (expand → contract) để tầng C luôn dùng được.
- Đổi mô hình embedding (`EMBEDDING_DIM`) không rollback được bằng tầng C; theo Database_Design §5.3.

## 4. Sau rollback

1. `make smoke` trên môi trường đích.
2. Mở incident record (`docs/10-operations/incidents/`), kể cả khi rollback thành công.
3. Không deploy lại tới khi post-incident review có hành động sửa đã merge.

## 5. Diễn tập

| Ngày | Môi trường | Tầng | Kết quả |
|---|---|---|---|
| 2026-10-27 | Cục bộ (Homebrew) | D — sao lưu → khôi phục `cwd_restore_drill` | Đạt: số tài liệu/đoạn khớp, đối soát sạch (`runbook.md`) |
| 2026-10-27 | Cục bộ (Colima, `make prod-up`) | C — thay từng bản api (`rolling-test.sh`) | Đạt 7/7, không rơi yêu cầu |
| — | **Môi trường đích** | A, B, C, D | **Chưa** — điều kiện R9 |
