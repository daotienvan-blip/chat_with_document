# Spike S3-00 — HNSW so với quét chính xác khi có điều kiện lọc

> Ngày: 2026-10-27 · Script: `app/server/scripts/spike_hnsw.py` (`make spike`) · Môi trường: PostgreSQL 17.11 (Homebrew, macOS arm64), pgvector 0.8.7.
> Dữ liệu: 40.000 đoạn ngẫu nhiên trong 200 tài liệu, 10% tài liệu `processing`, 10% đã xóa mềm; 100 truy vấn ngẫu nhiên; top-20.

## Kết quả

**384 chiều** (cấu hình demo hiện tại):

| Chế độ | ef_search | Quét lặp | p50 ms | p95 ms | Dòng trả về (min/TB) | Recall@20 so với exact |
|---|---|---|---|---|---|---|
| exact | — | không | 24.6 | 27.0 | 20/20.0 | 1.000 |
| hnsw | 40 | không | 2.4 | 21.5 | 20/20.0 | 0.114 |
| hnsw | 100 | không | 3.3 | 4.0 | 20/20.0 | 0.243 |
| hnsw | 200 | không | 5.5 | 6.8 | 20/20.0 | 0.376 |
| hnsw | 40 | có | 1.5 | 1.9 | 20/20.0 | 0.114 |
| hnsw | 100 | có | 3.1 | 3.6 | 20/20.0 | 0.243 |

**64 chiều** (cấu hình kiểm thử): exact p95 8.7 ms; HNSW ef=200 recall 0.910.

## Quyết định

- **`RETRIEVAL_MODE=exact` là mặc định.** Quét chính xác đạt p95 27 ms ở 40.000 đoạn — dưới mục tiêu DQ-03 (≤ 100 ms) — và luôn trả đủ dòng, recall tuyệt đối.
- HNSW nhanh hơn 5–10 lần nhưng recall rất thấp trên dữ liệu này. Không chọn HNSW cho tới khi đo lại với **vector thật** (OQ-S01) và quy mô thật (OQ-001).
- Không có trường hợp trả thiếu dòng khi lọc (pgvector 0.8.7) — rủi ro ở Database_Design §3.4.5 không xuất hiện ở quy mô này.
- Giữ chỉ mục HNSW trong `schema.sql` (không tạo migration 0002) để chuyển chế độ bằng cấu hình khi cần; chi phí là thời gian ghi chỉ mục khi xử lý tài liệu.

## Giới hạn

Vector ngẫu nhiên là trường hợp xấu nhất cho chỉ mục xấp xỉ; recall trên embedding thật thường cao hơn nhiều. Kết quả chỉ nói về độ trễ và số dòng, không nói về chất lượng ngữ nghĩa. Đo trên một máy phát triển, không phải máy chủ đích.
