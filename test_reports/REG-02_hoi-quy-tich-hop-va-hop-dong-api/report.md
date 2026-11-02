# Test report – REG-02: Hồi quy tích hợp và hợp đồng API

| Trường | Giá trị |
|---|---|
| Test case | [REG-02](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.7 |
| Mục tiêu (test plan) | Tích hợp + hợp đồng API trên PostgreSQL thật: 100% đạt |
| Kết luận | **ĐẠT** |
| Bắt đầu | 2026-11-02T12:14:58.326Z |
| Kết thúc | 2026-11-02T12:15:46.782Z (48.5 s) |
| Cách thực hiện | Tự động – pytest `-m integration` trên PostgreSQL 17 + pgvector thật; S3 SeaweedFS của `make up` |
| URL ứng dụng | — |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |
| Thư mục chạy | app/server |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | `test_schema_constraints` (integration/test_flows) | Test đạt | passed (0.22 s) | Đạt | [log](logs/02-pytest.log) |
| 2 | `test_upload_list_get` (integration/test_flows) | Test đạt | passed (0.21 s) | Đạt | [log](logs/02-pytest.log) |
| 3 | `test_upload_rejections` (integration/test_flows) | Test đạt | passed (0.04 s) | Đạt | [log](logs/02-pytest.log) |
| 4 | `test_upload_atomic_on_failures` (integration/test_flows) | Test đạt | passed (0.04 s) | Đạt | [log](logs/02-pytest.log) |
| 5 | `test_job_queue_concurrency_and_backoff` (integration/test_flows) | Test đạt | passed (0.03 s) | Đạt | [log](logs/02-pytest.log) |
| 6 | `test_ingestion_outcomes[ready]` (integration/test_flows) | Test đạt | passed (0.17 s) | Đạt | [log](logs/02-pytest.log) |
| 7 | `test_ingestion_outcomes[corrupt]` (integration/test_flows) | Test đạt | passed (0.15 s) | Đạt | [log](logs/02-pytest.log) |
| 8 | `test_ingestion_outcomes[encrypted]` (integration/test_flows) | Test đạt | passed (0.20 s) | Đạt | [log](logs/02-pytest.log) |
| 9 | `test_ingestion_outcomes[image-only]` (integration/test_flows) | Test đạt | passed (0.17 s) | Đạt | [log](logs/02-pytest.log) |
| 10 | `test_ingestion_extractor_crash_is_processing_error` (integration/test_flows) | Test đạt | passed (0.04 s) | Đạt | [log](logs/02-pytest.log) |
| 11 | `test_ingestion_idempotent_and_deleted_midway` (integration/test_flows) | Test đạt | passed (0.58 s) | Đạt | [log](logs/02-pytest.log) |
| 12 | `test_ingestion_ai_retry_then_terminal` (integration/test_flows) | Test đạt | passed (0.61 s) | Đạt | [log](logs/02-pytest.log) |
| 13 | `test_ask_answered_with_sources` (integration/test_flows) | Test đạt | passed (0.33 s) | Đạt | [log](logs/02-pytest.log) |
| 14 | `test_not_found_paths` (integration/test_flows) | Test đạt | passed (0.19 s) | Đạt | [log](logs/02-pytest.log) |
| 15 | `test_multi_doc_sources` (integration/test_flows) | Test đạt | passed (0.48 s) | Đạt | [log](logs/02-pytest.log) |
| 16 | `test_partial_requires_sources` (integration/test_flows) | Test đạt | passed (0.18 s) | Đạt | [log](logs/02-pytest.log) |
| 17 | `test_question_validation` (integration/test_flows) | Test đạt | passed (0.04 s) | Đạt | [log](logs/02-pytest.log) |
| 18 | `test_ai_errors_mapped` (integration/test_flows) | Test đạt | passed (0.20 s) | Đạt | [log](logs/02-pytest.log) |
| 19 | `test_source_pages_match` (integration/test_flows) | Test đạt | passed (0.21 s) | Đạt | [log](logs/02-pytest.log) |
| 20 | `test_file_endpoint` (integration/test_flows) | Test đạt | passed (0.19 s) | Đạt | [log](logs/02-pytest.log) |
| 21 | `test_delete_is_immediate_everywhere` (integration/test_flows) | Test đạt | passed (0.19 s) | Đạt | [log](logs/02-pytest.log) |
| 22 | `test_purge_order_and_race` (integration/test_flows) | Test đạt | passed (0.27 s) | Đạt | [log](logs/02-pytest.log) |
| 23 | `test_race_deleted_between_retrieve_and_sources` (integration/test_flows) | Test đạt | passed (0.19 s) | Đạt | [log](logs/02-pytest.log) |
| 24 | `test_busy_and_rate_limit` (integration/test_flows) | Test đạt | passed (0.05 s) | Đạt | [log](logs/02-pytest.log) |
| 25 | `test_reconcile` (integration/test_flows) | Test đạt | passed (0.18 s) | Đạt | [log](logs/02-pytest.log) |
| 26 | `test_observability_no_content_leak` (integration/test_flows) | Test đạt | passed (0.19 s) | Đạt | [log](logs/02-pytest.log) |
| 27 | `test_api_and_worker_privileges` (integration/test_privileges) | Test đạt | passed (0.04 s) | Đạt | [log](logs/02-pytest.log) |
| 28 | `test_readyz_queries_work_under_least_privilege` (integration/test_privileges) | Test đạt | passed (0.01 s) | Đạt | [log](logs/02-pytest.log) |
| 29 | `test_s3_store_roundtrip` (integration/test_s3_store) | Test đạt | passed (21.76 s) | Đạt | [log](logs/02-pytest.log) |
| 30 | `test_s3_store_unavailable_maps_to_domain_error` (integration/test_s3_store) | Test đạt | passed (0.01 s) | Đạt | [log](logs/02-pytest.log) |

## Log

- [01-setup.log](logs/01-setup.log)
- [02-pytest.log](logs/02-pytest.log)
- [03-teardown.log](logs/03-teardown.log)

## Ghi chú / lỗi phát hiện

- Mọi phản hồi API trong các test tích hợp được kiểm theo `docs/04-design/openapi.yaml` (`tests/support/openapi_assert.py`).
