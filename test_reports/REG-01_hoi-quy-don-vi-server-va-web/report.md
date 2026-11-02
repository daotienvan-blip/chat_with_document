# Test report – REG-01: Hồi quy đơn vị server và web

| Trường | Giá trị |
|---|---|
| Test case | [REG-01](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.7 |
| Mục tiêu (test plan) | Đơn vị server + web: 100% đạt |
| Kết luận | **ĐẠT** |
| Bắt đầu | 2026-11-02T12:14:53.750Z |
| Kết thúc | 2026-11-02T12:14:58.324Z (4.6 s) |
| Cách thực hiện | Tự động – pytest (đơn vị, `-m "not integration"`) và vitest |
| URL ứng dụng | — |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |
| Thư mục chạy | app/server; app/web |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | `test_hash_embedding_similarity` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 2 | `test_extractive_cites_and_not_found` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 3 | `test_extractive_accents_def001` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 4 | `test_http_llm_ok_and_dim_check` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 5 | `test_http_llm_errors[503-AiUnavailable]` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 6 | `test_http_llm_errors[429-AiUnavailable]` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 7 | `test_http_llm_errors[400-ConfigurationError]` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 8 | `test_http_llm_errors[timeout-AiTimeout]` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 9 | `test_http_llm_errors[conn-AiUnavailable]` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 10 | `test_http_llm_errors[garbage-AiBadOutput]` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 11 | `test_resilient_retry_then_breaker` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 12 | `test_memory_store_range_and_delete` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 13 | `test_pdf_extractor_cases` (unit/test_adapters) | Test đạt | passed (0.89 s) | Đạt | [log](logs/01-pytest.log) |
| 14 | `test_pdf_extractor_crash_is_not_corrupt[1-Traceback (most recent call last):\n  ...\nMemo…` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 15 | `test_pdf_extractor_crash_is_not_corrupt[1-ImportError: lib.so: failed to map segment from…` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 16 | `test_pdf_extractor_crash_is_not_corrupt[-9--SIGKILL]` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 17 | `test_pdf_extractor_crash_is_not_corrupt[3-van ban tai lieu-exit3]` (unit/test_adapters) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 18 | `test_upload_exact_limit_ok_one_byte_over_rejected` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 19 | `test_upload_rejects_non_pdf[%PDF-1.7\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx…` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 20 | `test_upload_rejects_non_pdf[MZ\x90\x00xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-…` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 21 | `test_upload_rejects_non_pdf[-rong.pdf]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 22 | `test_upload_missing_file` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 23 | `test_upload_hash_and_stops_early` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 24 | `test_sanitize_name[../../etc/passwd.pdf-passwd.pdf]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 25 | `test_sanitize_name[C:\\x\\h\u1ee3p \u0111\u1ed3ng.pdf-h\u1ee3p \u0111\u1ed3ng.pdf]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 26 | `test_sanitize_name[-tai-lieu.pdf]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 27 | `test_sanitize_name[a\x00b.pdf-ab.pdf]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 28 | `test_chunker_properties` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 29 | `test_chunker_empty_and_deterministic` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 30 | `test_chunker_char_cap` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 31 | `test_rrf_and_cap` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 32 | `test_tsquery_safe[\u0110i\u1ec1u kho\u1ea3n 'thanh to\xe1n' & ph\u1ea1t \| ! : * ( )]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 33 | `test_tsquery_safe[]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 34 | `test_tsquery_safe[???]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 35 | `test_tsquery_safe[a_b ca_b ca_b ca_b ca_b ca_b ca_b ca_b ca_b ca_b ca_b ca_b ca_b ca_b ca…` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 36 | `test_prompt_marks_data_block` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 37 | `test_prompt_rules_conflict_and_language` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 38 | `test_grounding_validator[out0-answered-2]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 39 | `test_grounding_validator[out1-not_found-0]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 40 | `test_grounding_validator[out2-not_found-0]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 41 | `test_grounding_validator[out3-not_found-0]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 42 | `test_grounding_validator[out4-not_found-0]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 43 | `test_grounding_validator[out5-partial-1]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 44 | `test_grounding_validator[out6-not_found-0]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 45 | `test_parse_output_rejects[not json]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 46 | `test_parse_output_rejects[[]]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 47 | `test_parse_output_rejects[{"status":"answered","answer":"x"}]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 48 | `test_parse_output_rejects[raw3]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 49 | `test_parse_output_rejects[raw4]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 50 | `test_parse_output_rejects[raw5]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 51 | `test_parse_output_rejects[raw6]` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 52 | `test_load_guard_busy_after_wait` (unit/test_core_units) | Test đạt | passed (0.05 s) | Đạt | [log](logs/01-pytest.log) |
| 53 | `test_rate_limiter_bucket_and_recovery` (unit/test_core_units) | Test đạt | passed (0.00 s) | Đạt | [log](logs/01-pytest.log) |
| 54 | `[US-006-AC2] kho trống: hướng dẫn tải và khóa khung hỏi` (src/app/app.test.tsx) | Test đạt | passed (0.07 s) | Đạt | [log](logs/02-vitest.log) |
| 55 | `[US-002-AC2][US-003-AC2] trạng thái có chữ, lý do lỗi và tài liệu chưa sẵn sàng` (src/app/app.test.tsx) | Test đạt | passed (0.02 s) | Đạt | [log](logs/02-vitest.log) |
| 56 | `[US-001-AC3] tệp không phải PDF bị từ chối, không tạo dòng` (src/app/app.test.tsx) | Test đạt | passed (0.03 s) | Đạt | [log](logs/02-vitest.log) |
| 57 | `[US-006-AC1][US-007-AC1][US-008-AC1] hỏi, hiển thị nguồn dạng chip mở đúng trang; giữ qua…` (src/app/app.test.tsx) | Test đạt | passed (0.12 s) | Đạt | [log](logs/02-vitest.log) |
| 58 | `[US-010-AC1][US-010-AC2] không tìm thấy và trả lời một phần có kiểu hiển thị riêng` (src/app/app.test.tsx) | Test đạt | passed (0.09 s) | Đạt | [log](logs/02-vitest.log) |
| 59 | `[EC-07] lỗi AI giữ câu hỏi, đếm ngược Retry-After rồi gửi lại` (src/app/app.test.tsx) | Test đạt | passed (0.15 s) | Đạt | [log](logs/02-vitest.log) |
| 60 | `[US-005-AC1] hộp thoại xóa: focus vào Hủy, Esc đóng, xác nhận gọi DELETE` (src/app/app.test.tsx) | Test đạt | passed (0.07 s) | Đạt | [log](logs/02-vitest.log) |
| 61 | `ánh xạ lỗi: mã lạ ⇒ lỗi chung có mã tham chiếu; lỗi trường không thử lại` (src/app/app.test.tsx) | Test đạt | passed (0.00 s) | Đạt | [log](logs/02-vitest.log) |

## Log

- [01-pytest.log](logs/01-pytest.log)
- [02-vitest.log](logs/02-vitest.log)

## Ghi chú / lỗi phát hiện

- (không có)
