# Trạng thái triển khai — 2026-10-27

> Mã nguồn: `app/` (server Python, web React, deploy). Cách chạy: `app/README.md`, `runbook.md`.
> Trạng thái được đánh giá trung thực theo **Tiêu chí hoàn thành** của từng task: ✅ xong · 🟡 một phần (nêu rõ thiếu gì) · ⛔ chưa làm / bị chặn.

## Tổng quan

| Hạng mục | Kết quả đã chạy trên máy dev (macOS arm64) |
|---|---|
| `make check` | ruff sạch; import-linter 3/3 hợp đồng giữ; **48** test đơn vị server; typecheck + **8** test web |
| `make prod-up` + `make proxy-test` | Stack kiểu sản xuất trên Colima; proxy 13/13; `rolling-test.sh` 7/7; smoke 17/17 qua HTTPS |
| `make test-int` | **29** test tích hợp (gồm 2 test adapter S3 — tự bỏ qua khi không có `make up`) trên PostgreSQL 17 + pgvector 0.8.7 thật; mọi phản hồi API trong test được kiểm theo `openapi.yaml` |
| `make smoke` | **17/17** bước đầu-cuối trên hệ thống đang chạy (tải PDF → sẵn sàng → hỏi có nguồn → mở nguồn → nhiều tài liệu → ngoài tài liệu → PDF mật khẩu → tệp sai → xóa) |
| `make eval` | Bộ tổng hợp 15 câu, AI giả trích xuất: **80%** câu ngoài tài liệu → `not_found` (q15 thêm 2026-10-28 lộ DEF-001); 100% nguồn đúng tài liệu/trang. **Bộ nhỏ và đã được dùng để chỉnh AI giả — không phản ánh chất lượng mô hình thật** |
| `make trace` | 22/23 AC của USER_STORIES có test; US-015-AC1 chỉ có bằng chứng tài liệu (chờ OQ-005) |
| Spike S3-00 | Quét chính xác p95 27 ms ở 40.000 đoạn/384 chiều ⇒ giữ `exact` (`notes/spike-hnsw.md`) |
| Khôi phục thử | Sao lưu → khôi phục → khớp số liệu, đối soát sạch (`runbook.md`) |

## Khác biệt so với PLAN (có chủ đích)

| Khác biệt | Lý do |
|---|---|
| Mã nằm trong `app/` thay vì gốc dự án | Theo yêu cầu người dùng |
| Bản demo chạy trên PostgreSQL Homebrew + kho tệp cục bộ (`LocalFsObjectStore`) | Người dùng chọn cài bằng Homebrew. Stack Docker (`make up`, Colima) đã chạy được từ S0-02 và dùng song song qua cổng 5433/9000 |
| SeaweedFS thay MinIO làm S3 dev | MinIO ngừng phát hành ảnh Docker công khai (`minio/minio`, `quay.io/minio/*` không pull được) |
| Proxy dùng `nginx-unprivileged` (cổng 8443), trang lỗi trả bằng `return` có `requestId` thật | Không chạy bằng root; bản trước trả `requestId` rỗng |
| `/readyz` kiểm quyền INSERT trên `jobs` thay vì đọc hàng đợi | `cwd_api` không có SELECT trên `jobs` ⇒ bản cũ luôn 503 khi chạy đúng phân quyền (tìm thấy ở S8-05) |
| Lifecycle bucket: xóa phiên bản cũ sau 7 ngày | Versioning (Database_Design §5.2) khiến PDF đã xóa còn lại **vô thời hạn**; quy tắc đưa về đúng giới hạn 7 ngày của OQ-D01. Chưa kiểm chứng việc xóa thực tế |
| AI giả trích xuất (`ExtractiveLlm`) thay cho dịch vụ AI | Không có khóa AI; người dùng chọn. Adapter HTTP tương thích OpenAI có sẵn, bật bằng `LLM_PROVIDER=http` |
| ~~Không dùng mypy, không có tệp CI~~ → đã bổ sung ở giai đoạn 7 (2026-10-28) | `.github/workflows/ci.yml` + `make ci`: ruff, mypy (sửa 8 lỗi), import-linter, coverage ≥ 70%, gitleaks, build ảnh — xem `docs/07-verification/` |
| Web test dùng `fetch` giả thay cho MSW | Ít phụ thuộc hơn; cùng mục đích |
| E2E bằng `scripts/smoke.py` (HTTP) thay cho Playwright | Chưa có trình duyệt tự động trên máy; giao diện được kiểm bằng test thành phần |
| `GET …/file` có thêm `304` (If-None-Match) | Đã bổ sung vào `openapi.yaml` và `API_Design.md` (thay đổi cộng thêm) |
| Một lỗi tìm được khi triển khai: PDF trích ra dùng khoảng trắng không ngắt (`\xa0`) và gạch nối mềm | Chuẩn hóa NFKC trong extractor, nếu không FTS và tách câu sai |

## Từng task

| Task | Trạng thái | Ghi chú / còn thiếu |
|---|---|---|
| S0-01 | ✅ | `app/Makefile`; marker `integration`, `req`. Không mypy/CI |
| S0-02 | ✅ | `make up` trên Colima: PostgreSQL+pgvector (cổng 5433) + SeaweedFS S3 (cổng 9000) **healthy**; 28/28 test tích hợp + smoke 17/17 trên stack này. Bản demo vẫn dùng Homebrew (5432) |
| S0-03 | ✅ | Cấu hình, log JSON, problem+json 12 mã, `/config`, `/healthz`, `/readyz` |
| S0-04 | ✅ | Alembic 0001 thực thi `schema.sql`; test từng ràng buộc |
| S0-05 | ✅ | Cổng, kiểu miền, `FakeLlm`, kho bộ nhớ, composition root (`cwd_server/container.py`) |
| S0-06 | ✅ | Quy tắc phụ thuộc (đã thử vi phạm → BROKEN). Adapter S3: `test_s3_store.py` 2/2 trên SeaweedFS; sửa lỗi `check()` khi thiếu bucket |
| S0-07 | ✅ | Khung web, token từ `html_design`, kiểu sinh từ OpenAPI |
| S1-01 → S1-05 | ✅ | Kiểm tra tệp, tải lên nguyên tử + bù trừ, API, danh sách + polling, tải lên có tiến độ/hủy/thử lại |
| S2-01 | ✅ | Tiến trình con có hạn thời gian. Giới hạn bộ nhớ **chưa kiểm chứng** trên macOS |
| S2-02 → S2-04 | ✅ | Chunker, hàng đợi (đồng thời, backoff, hoàn lần thử), xử lý tài liệu (idempotent, xóa giữa chừng) |
| S2-05 | 🟡 | Worker, vòng quét, SIGTERM dừng êm. Chưa có test tự động cho kill -9 giữa chừng (chỉ test `release_overdue`) |
| S2-06 | ✅ | Lý do lỗi, thông báo sẵn sàng, khóa khung hỏi |
| S3-00 | ✅ | `notes/spike-hnsw.md` |
| S3-01 → S3-03 | ✅ | Truy xuất lai + RRF + giới hạn/tài liệu; lời nhắc + G-L2; AnswerService G-L1/G-L2/G-L3, test race xóa |
| S3-04 | 🟡 | Adapter HTTP kiểm bằng MockTransport; **chưa gọi nhà cung cấp thật** (chặn OQ-005, OQ-S01) |
| S3-05, S3-06 | ✅ | |
| S4-01 | ✅ | Trang đúng; lưu ý: trang = phạm vi trang của đoạn (đoạn ~600 từ có thể trải 2 trang) |
| S4-02 | ✅ | Range/206/416/304/ETag. Chưa đo bộ nhớ với tệp 100 MB |
| S4-03 | 🟡 | Chip nguồn + test. **Chưa thử tay `#page=N` trên trình duyệt** (OQ-P09) |
| S5-01, S5-02 | ✅ | OQ-A03 (trường `missing`) chưa quyết định ⇒ không đổi hợp đồng |
| S6-01 → S6-03 | ✅ | Xóa mềm, purge đúng thứ tự, race, hộp thoại tiếp cận |
| S7-01 → S7-04 | ✅ | LoadGuard + rate limit; retry + breaker; lỗi UI + đếm ngược; đối soát |
| S8-01 | ✅ | `/metrics`, `/readyz` thật, test canary không lộ nội dung. Không có OpenTelemetry (tùy chọn) |
| S8-02 | ✅ | Test chạy bằng vai trò đăng nhập thật, 11 thao tác bị cấm bị từ chối |
| S8-03 | 🟡 | Phản hồi trong mọi test tích hợp được kiểm theo OpenAPI; **chưa có bộ duyệt hệ thống mọi thao tác × mã** hay Schemathesis |
| S8-04 | ✅ | Công cụ + bộ tổng hợp + CSV cho người chấm. G3 chặn OQ-004/DEP-002 |
| S8-05 | ✅ | `make prod-up`: 2 api + worker + proxy healthy, smoke 17/17 qua HTTPS; nâng cấp cuốn chiếu 7/7; không root, không lộ bí mật, worker cô lập mạng. Sửa 2 lỗi (readyz dưới quyền tối thiểu, đường dẫn Dockerfile) |
| S8-06 | ✅ | `make proxy-test` 13/13: TLS, tiêu đề, ghi đè X-Request-Id, 413/429/502 `problem+json` có requestId thật, allowlist, `/metrics` |
| S8-07 | ✅ | Sao lưu/khôi phục đã chạy thử; runbook; `DATA_LOCATION.md` (chữ ký trống, chờ OQ-005) |
| S8-08 | ⛔ | Playwright + axe chưa làm; thay tạm bằng `smoke.py` + test thành phần |
| S8-09 | ⛔ | Bị chặn OQ-A02 |
| S8-10 | ✅ | `release-gates.md`, `make trace` |

## Việc tiếp theo đề xuất

1. Mở http://localhost:8000 và thử bằng tay (giao diện chưa được kiểm trên trình duyệt thật).
2. Quyết định OQ-005/OQ-S01 rồi bật `LLM_PROVIDER=http`, chạy lại `make eval` với bộ câu hỏi thật (DEP-002).
3. Thêm Playwright + axe (S8-08) và bộ hợp đồng đầy đủ (S8-03).
4. Triển khai lên hạ tầng thật (OQ-005): PostgreSQL/S3 được quản lý, chứng chỉ thật, bộ quản lý bí mật, dải allowlist của tổ chức.
