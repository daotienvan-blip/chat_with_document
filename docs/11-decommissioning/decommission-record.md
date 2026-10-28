# Decommission record — "Chat với tài liệu"

> **Trạng thái:** **chưa kích hoạt** — chưa có quyết định cho nghỉ hưu. Tệp này là kế hoạch kèm bản kiểm kê thật ngày 2026-10-28, để nghỉ hưu có kế hoạch khi MVP kết thúc (không đạt giả thuyết, hoặc được thay bằng bản chính thức).
> Agent kiểm kê (chỉ đọc) và chuẩn bị checklist; **không xóa, không thu hồi**. Người thực hiện và ký: chủ sở hữu `[TBD: OQ-007]`.

## 1. Bên phụ thuộc (dependents)

| Bên | Phụ thuộc vào gì | Việc khi nghỉ hưu |
|---|---|---|
| Người dùng kinh doanh (UC-P1, UC-P2) | Giao diện web, tài liệu đã tải | Báo trước ≥ 2 tuần; hướng dẫn tải lại PDF gốc (ứng dụng không phải nơi lưu chính) |
| Hệ thống khác | **Không có** — không có API công khai, tích hợp hay webhook (sơ đồ use case: chỉ IF-02, IF-03) | — |
| Dịch vụ AI (IF-02) | Khóa API (nếu đã bật `LLM_PROVIDER=http`) | Thu hồi khóa; yêu cầu nhà cung cấp xóa dữ liệu theo điều khoản |
| Kho lưu trữ (IF-03) | Bucket S3 | Xóa theo §3 |
| Tài liệu dự án | `docs/`, `guide/`, sơ đồ | Cập nhật theo §5 |

## 2. Kiểm kê dữ liệu và tài nguyên (2026-10-28, máy phát triển)

| Tài nguyên | Vị trí | Chứa | Kích thước |
|---|---|---|---|
| CSDL demo | PostgreSQL Homebrew `/opt/homebrew/var/postgresql@17`, CSDL `cwd`, `cwd_test`, `cwd_restore_drill` | Siêu dữ liệu, đoạn văn bản tài liệu, vector | — |
| Tệp demo | `app/var/storage/` | PDF gốc | 4,6 MB |
| Sao lưu | `app/var/backups/` | Bản dump CSDL (có nội dung tài liệu) | 20 KB |
| Log | `app/var/log/` | Không có nội dung (test canary) | 8 KB |
| Kết quả CI/eval | `app/var/ci/`, `var/coverage/`, `var/eval/` | Báo cáo; `var/eval` có câu hỏi tổng hợp | ~1,1 MB |
| Bí mật stack cục bộ | `app/var/prod-local/compose.env`, `certs/` (khóa TLS tự ký) | Mật khẩu CSDL/S3 sinh ngẫu nhiên | 16 KB |
| Volume Docker | `cwd-dev_pgdata`, `cwd-dev_s3data`, `cwd-prod_prod-pgdata`, `cwd-prod_prod-s3data` | CSDL + PDF của 2 stack | — |
| Container | 8 đang chạy (`cwd-prod-*` ×6 kể cả đã dừng, `cwd-dev-*` ×2) | — | — |
| Ảnh | `cwd-server:local`, `cwd-server:ci`, `cwd-proxy:local`, `cwd-web:ci` + ảnh nền | Mã | — |
| Máy ảo | Colima | Mọi volume ở trên | — |
| Repo | `github.com/daotienvan-blip/chat_with_document` | Mã, tài liệu, lịch sử | — |
| Sản xuất | **Chưa có** — điền khi triển khai (OQ-005) | | |

## 3. Lưu giữ và xóa dữ liệu (verify)

Chính sách lưu giữ chưa chốt (OQ-005, OQ-D01). Tới khi có chính sách: **không xóa sao lưu trước khi chủ sở hữu ký §6**.

| # | Bước | Cách xác minh | Kết quả |
|---|---|---|---|
| D1 | Xuất danh sách tài liệu (tên, ngày tải) để lưu hồ sơ — **không** xuất nội dung | `GET /api/v1/documents` | |
| D2 | Xóa mọi tài liệu qua ứng dụng (đi đúng đường purge: tệp trước, bản ghi sau) | `SELECT count(*) FROM documents` = 0; bucket rỗng | |
| D3 | Xóa phiên bản cũ của bucket (versioning giữ tới 7 ngày) | Liệt kê object versions = 0 | |
| D4 | Xóa bản sao lưu theo chính sách (OQ-D01) | `var/backups/` + sao lưu sản xuất rỗng | |
| D5 | Drop CSDL `cwd`, `cwd_test`, `cwd_restore_drill`; xóa volume Docker | `\l`; `docker volume ls` | |
| D6 | Xóa `app/var/` | thư mục không tồn tại | |
| D7 | Yêu cầu nhà cung cấp AI xóa dữ liệu (nếu đã dùng `http`) | Xác nhận bằng văn bản | |

## 4. Thu hồi truy cập và thông tin xác thực

| # | Thông tin xác thực | Thu hồi | Xong |
|---|---|---|---|
| C1 | Vai trò CSDL `cwd_owner`, `cwd_api_login`, `cwd_worker_login` (và nhóm `cwd_api`, `cwd_worker`) | `DROP ROLE` sau D5 | ☐ |
| C2 | Khóa truy cập S3 (`compose.env` cục bộ; bộ quản lý bí mật ở sản xuất) | Vô hiệu hóa khóa | ☐ |
| C3 | Khóa API dịch vụ AI (nếu có) | Thu hồi ở nhà cung cấp | ☐ |
| C4 | Chứng chỉ TLS + khóa riêng | Thu hồi (chứng chỉ thật); xóa tệp | ☐ |
| C5 | Allowlist proxy, bản ghi DNS | Gỡ | ☐ |
| C6 | Quyền ghi repo, token/secret trong GitHub Actions | Gỡ cộng tác viên, xóa secret; **lưu trữ (archive) repo**, không xóa | ☐ |

## 5. Cập nhật sơ đồ và tài liệu

- `docs/diagrams/use-case-diagram.drawio` + `.md`: đánh dấu hệ thống đã nghỉ hưu.
- `docs/01-intake/intent.md`, `docs/03-analysis/PRD.md`: trạng thái "Retired", lý do, kết quả giả thuyết MVP.
- `app/README.md`, `guide/`: ghi chú đầu trang "đã nghỉ hưu ngày …".
- `app/deploy/DATA_LOCATION.md`: ghi ngày xóa từng loại dữ liệu.

## 6. Ký nghỉ hưu (chủ sở hữu điền)

| Vai trò | Tên | Xác nhận | Ngày |
|---|---|---|---|
| Chủ sở hữu sản phẩm | `[TBD: OQ-007]` | ☐ Đồng ý nghỉ hưu; D1–D7, C1–C6 đã xong | |
| CNTT / bảo mật | `[TBD: OQ-007]` | ☐ Thu hồi xác thực đã kiểm | |
| Pháp lý (nếu có dữ liệu thật) | `[TBD: OQ-007]` | ☐ Lưu giữ/xóa theo chính sách | |
