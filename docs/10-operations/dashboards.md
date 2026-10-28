# Dashboard và dải kiểm soát — "Chat với tài liệu"

> Nguồn số liệu: `GET /metrics` của từng bản api (Prometheus; proxy chặn từ ngoài — trả 403, đã kiểm 2026-10-28), log JSON (`platform/logging.py`, chỉ trường cho phép). Định nghĩa metrics: `app/server/cwd_server/platform/metrics.py`.
> **Chưa có Prometheus/Grafana được triển khai.** Tệp này là đặc tả để dựng dashboard trên hạ tầng thật.

## 1. Bảng (panel)

| # | Panel | PromQL |
|---|---|---|
| P1 | Tỷ lệ lỗi 5xx | `sum(rate(cwd_http_requests_total{status=~"5.."}[5m])) / sum(rate(cwd_http_requests_total[5m]))` |
| P2 | Độ trễ p95 hỏi đáp | `histogram_quantile(0.95, sum by (le) (rate(cwd_http_request_seconds_bucket{route="/api/v1/questions"}[5m])))` |
| P3 | Câu trả lời theo trạng thái | `sum by (status) (rate(cwd_answers_total[1h]))` |
| P4 | Tỷ lệ "không tìm thấy" | `sum(rate(cwd_answers_total{status="not_found"}[1h])) / sum(rate(cwd_answers_total[1h]))` |
| P5 | G-L2 hạ cấp (AI trích nguồn sai) | `increase(cwd_grounding_downgrades_total[1h])` |
| P6 | Lỗi gọi AI | `sum by (op) (rate(cwd_llm_calls_total{outcome!="ok"}[5m])) / sum by (op) (rate(cwd_llm_calls_total[5m]))` |
| P7 | Circuit breaker | `max(cwd_llm_breaker_open)` |
| P8 | Hàng đợi theo trạng thái | `cwd_jobs` — **xem OBS-1** |
| P9 | Việc chờ lâu nhất | `cwd_oldest_queued_job_seconds` — **xem OBS-1** |
| P10 | Bị giới hạn / quá tải | `sum by (status) (rate(cwd_http_requests_total{status=~"429\|503"}[5m]))` |
| P11 | Sẵn sàng | probe `GET /readyz` mỗi 30 s từ ngoài cụm |

## 2. Dải kiểm soát (control band)

Giá trị là **đề xuất** cho MVP (PRD đã loại NFR hiệu năng/độ tin cậy — v0.6); release owner chốt trước giai đoạn 2. "Vàng" = theo dõi, ghi nhận. "Đỏ" = mở incident (`incidents/README.md`), xét rollback.

| Chỉ số | Bình thường | Vàng | Đỏ |
|---|---|---|---|
| P1 lỗi 5xx | < 1% | 1–5% trong 10 phút | > 5% trong 5 phút |
| P2 p95 hỏi đáp | < 10 s | 10–30 s | > 30 s (hết thời gian gọi AI) |
| P4 "không tìm thấy" | trong ±2σ của 7 ngày trước | lệch > 2σ | 0% trong 1 ngày có ≥ 20 câu (nghi DEF-001 tái phát: không còn từ chối) hoặc 100% (truy xuất hỏng) |
| P5 G-L2 hạ cấp | 0–2/giờ | > 2/giờ | > 10/giờ |
| P6 lỗi AI | < 2% | 2–10% | > 10% hoặc P7 = 1 quá 5 phút |
| P9 việc chờ lâu nhất | < 2 phút | 2–10 phút | > 10 phút (tài liệu kẹt — F-02) |
| P11 sẵn sàng | 2/2 bản api | 1/2 | 0/2 |
| Log `event=unhandled` | 0 | ≥ 1/giờ | ≥ 10/giờ |
| Log `event=missing_file` | 0 | — | ≥ 1 (dữ liệu mất đồng bộ) |

## 3. Ảnh chụp đường cơ sở — 2026-10-28 (stack cục bộ `make prod-up`, chạy 26 giờ, agent đọc, không thay đổi)

| Quan sát | Giá trị |
|---|---|
| `/healthz`, `/readyz` qua proxy và bản demo | 200 · 200 · 200 · 200 (≤ 0,13 s) |
| Container | api×2 healthy, worker, proxy, db healthy, s3 healthy; không khởi động lại |
| `cwd-prod-api-1` | 2.082 lượt `readyz` (healthcheck), 2 câu hỏi → 2 `not_found`, 0 G-L2 hạ cấp, 4 lời gọi AI đều `ok`, breaker đóng, 0 phản hồi 5xx |
| Log worker 26 giờ | 6 `reconcile`, 2 `document_purged`; 0 cảnh báo/lỗi |

Không có lưu lượng thật — đường cơ sở chỉ xác nhận việc thu thập hoạt động, không dùng để đặt dải.

## 4. Lỗ hổng giám sát (phải sửa trước giai đoạn 1 của `release-record.md` §5)

| Mã | Mức | Vấn đề | Bằng chứng | Đề xuất |
|---|---|---|---|---|
| **OBS-1** | Major | `cwd_jobs`, `cwd_oldest_queued_job_seconds`, `cwd_job_seconds` được cập nhật **trong tiến trình worker** (`worker/maintenance.py:41-42`, `worker/runner.py:68`), nhưng worker không mở cổng metrics ⇒ không ai thu được. Bản api trả `cwd_oldest_queued_job_seconds 0.0` (giá trị mặc định) — **trông như khỏe dù hàng đợi kẹt**. Kết hợp với F-02, tài liệu kẹt sẽ không được phát hiện | Đọc `/metrics` của `cwd-prod-api-1` 2026-10-28: không có dòng `cwd_jobs` | Worker gọi `prometheus_client.start_http_server` trên cổng nội bộ, hoặc bản api đọc số liệu hàng đợi từ CSDL khi được scrape; bỏ gauge khỏi registry của api |
| OBS-2 | Major | Chưa có Prometheus, Alertmanager, lưu log tập trung | — | Dùng hạ tầng giám sát của tổ chức (OQ-005) |
| OBS-3 | Minor | Phản hồi 429 trong ứng dụng không được đếm (F-04) | `review-record.md` F-04 | Sửa F-04 |
| OBS-4 | Minor | `/readyz` 503 không ghi lý do (F-05) | `review-record.md` F-05 | Sửa F-05 |
