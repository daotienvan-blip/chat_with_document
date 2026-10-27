# Vị trí dữ liệu — bằng chứng cho G8 / AC-016 / US-015

> Điền theo **môi trường thật** trước khi dùng dữ liệu thật. Bảng dưới đang ghi cấu hình **demo cục bộ** (2026-10-27).
> Chặn bởi OQ-005 (chính sách vị trí, lưu giữ, gửi nội dung tới AI bên ngoài) và OQ-D01 (dữ liệu đã xóa còn trong sao lưu).

| Dữ liệu | Nơi lưu (demo cục bộ) | Nơi lưu (sản xuất) | Mã hóa khi lưu | Thời hạn giữ |
|---|---|---|---|---|
| CSDL (siêu dữ liệu, đoạn văn bản, vector) | PostgreSQL 17 trên máy phát triển, `/opt/homebrew/var/postgresql@17` | `[TBD: OQ-005]` | Không (máy dev) — sản xuất: volume mã hóa `[TBD: OQ-P08]` | Tới khi xóa; xóa vật lý sau 1 giờ |
| PDF gốc | `app/var/storage/documents/` (hệ tệp cục bộ) | Bucket S3-compatible `[TBD: OQ-005]` | Không (máy dev) — sản xuất: SSE | Như trên |
| Bản sao lưu | `app/var/backups/` (7 bản) | `[TBD]` | `[TBD]` | 7 ngày — **dữ liệu đã xóa còn trong sao lưu tới 7 ngày (OQ-D01)** |
| Nhật ký ứng dụng | `app/var/log/` — không chứa nội dung câu hỏi/tài liệu (đã kiểm bằng test canary) | `[TBD]` | — | `[TBD]` |
| Gửi ra dịch vụ AI | **Không** — demo dùng AI giả chạy cục bộ (`LLM_PROVIDER=extractive`) | `[TBD: OQ-005]` — nếu bật `http`: câu hỏi + tối đa 8 đoạn mỗi lượt; đoạn văn bản khi xử lý tài liệu | — | Theo điều khoản nhà cung cấp |

## Phê duyệt

| Vai trò | Tên | Quyết định | Ngày |
|---|---|---|---|
| CNTT / bảo mật | `[TBD: OQ-007]` | ☐ Chấp thuận ☐ Từ chối | |
| Pháp lý | `[TBD: OQ-007]` | ☐ Chấp thuận ☐ Từ chối | |
