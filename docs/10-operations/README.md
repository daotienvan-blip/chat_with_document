# 10 — Vận hành

Chưa có production (OQ-005). Giám sát đã chạy thử trên stack cục bộ `make prod-up`.

| Tệp | Nội dung |
|---|---|
| `dashboards.md` | Panel PromQL, dải kiểm soát xanh/vàng/đỏ, ảnh chụp đường cơ sở 2026-10-28, lỗ hổng giám sát OBS-1…4 |
| `runbook.md` | Cảnh báo → kiểm gì → làm gì → leo thang; mức Sev1–3. Lệnh chi tiết: `docs/05-implement/runbook.md` |
| `incidents/README.md` | Quy trình incident → control band → intent mới → post-incident review → bài học; mẫu incident record |
| `incidents/INC-2026-10-28-01.md` | PR #1 merge khi CI đỏ, không review (+ intent khắc phục) |

Agent chỉ đọc telemetry/log và đề xuất; không thay đổi production.
