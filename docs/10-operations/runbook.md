# Runbook vận hành — theo cảnh báo

> Lệnh khởi động, sao lưu, khôi phục, cấu hình: `docs/05-implement/runbook.md`. Tệp này sắp theo **cảnh báo** ở `dashboards.md` §2.
> **Agent chỉ đọc** (metrics, log, trạng thái) và đề xuất; mọi thay đổi trên production do người trực thực hiện.

| Cảnh báo | Kiểm trước | Hành động | Leo thang |
|---|---|---|---|
| P11 `readyz` đỏ | `docker ps`; log api `event=unhandled`; CSDL nhận kết nối (`pg_isready`); kho S3 | Bản api lỗi: khởi động lại riêng bản đó. CSDL/S3 lỗi: xử lý phụ thuộc trước, api tự hồi phục | 0/2 bản quá 5 phút ⇒ Sev1, rollback tầng C nếu sau deploy |
| P1 5xx > 5% | Log `event=unhandled` (chỉ có tên lớp ngoại lệ); deploy gần nhất | Nếu trong 1 giờ sau deploy ⇒ rollback tầng C | Sev2 |
| P2 p95 > 30 s | P6, P7 (AI chậm?); CPU CSDL; số đoạn (> 40.000 ⇒ cân nhắc `RETRIEVAL_MODE=hnsw`) | AI chậm: chờ breaker; nếu kéo dài, báo nhà cung cấp | Sev3 |
| P4 "không tìm thấy" = 0% | Lấy mẫu 5 câu trả lời gần nhất (qua người dùng, **không** đọc nội dung từ log — log không có) | Nghi DEF-001 tái phát ⇒ báo release owner; cân nhắc tầng B (thu hẹp người dùng) | Sev2 nếu người dùng xác nhận câu trả lời bịa |
| P5 G-L2 hạ cấp > 10/giờ | Phiên bản/mô hình AI có đổi? | Tầng A (`LLM_PROVIDER=extractive`) nếu mô hình mới gây ra | Sev2 |
| P6/P7 AI lỗi, breaker mở | Trang trạng thái nhà cung cấp; khóa API hết hạn? | Không cần thao tác nếu tự hồi phục; người dùng thấy thông báo `AI_UNAVAILABLE` | Sev3; Sev2 nếu > 1 giờ |
| P9 việc chờ > 10 phút | Worker còn chạy? Log worker `job_retry`/`job_error`; tài liệu nào ở `processing` lâu | Khởi động lại worker. Nếu cùng một tài liệu làm worker chết lặp lại (**F-02**, chưa sửa): xóa tài liệu đó qua giao diện để dừng vòng lặp | Sev2 |
| `event=missing_file` | Kho S3 còn tệp? Lifecycle bucket | Đối soát tự chạy mỗi giờ đánh dấu `PROCESSING_ERROR`; người dùng tải lại | Sev2 nếu nhiều tài liệu |
| Nghi lộ dữ liệu | — | Tầng B ngay; xóa khẩn cấp theo `docs/05-implement/runbook.md`; báo CNTT/bảo mật | **Sev1** |

## Mức độ sự cố

| Mức | Định nghĩa | Thời gian phản hồi (đề xuất) |
|---|---|---|
| Sev1 | Không dùng được, hoặc lộ/mất dữ liệu | 15 phút |
| Sev2 | Chức năng chính sai (trả lời bịa, tài liệu kẹt hàng loạt) | 1 giờ |
| Sev3 | Chậm/suy giảm, có cách tránh | 1 ngày làm việc |
