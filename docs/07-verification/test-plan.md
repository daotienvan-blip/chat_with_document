# Kế hoạch kiểm thử tổng thể (Master Test Plan) — "Chat với tài liệu" (MVP)

> **Chuẩn:** IEEE 829-2008 (Master Test Plan). Khung theo `testPlan_prompt.md`; đối chiếu đủ 18 mục của `Test_Plan_IEEE_829_Checklist.xlsx` (bản đã điền: `Test_Plan_IEEE_829_Checklist.xlsx` cùng thư mục).
> **Quy ước:** giá trị `[TBD: OQ-xxx]` giữ nguyên, không bịa. "Tự động" = chạy trong CI (L0) hoặc lệnh `make`; "Thủ công" = người thực hiện có biên bản.
> **Kết quả thực thi:** xem `test-report.md`. Kết quả review mã: `review-record.md`.

---

## 1. Định danh kế hoạch (IEEE 829 §5.1)

| Thuộc tính | Giá trị |
|---|---|
| Mã tài liệu | **CWD-MTP-v1.0** |
| Phiên bản | 1.0 |
| Ngày phát hành | 2026-10-28 |
| Trạng thái | **Draft — chờ phê duyệt** (§16) |
| Phân loại | Nội bộ |
| Người soạn | Agent (Claude) — vai trò soạn thảo, không có quyền phê duyệt |
| Người phê duyệt | QA Lead / Product owner `[TBD: OQ-007]` |
| Mã nguồn được kiểm | `main` @ `ec18ff6` + thay đổi giai đoạn 7 (CI, sửa kiểu) — xem `test-report.md` §1 |

## 2. Giới thiệu (IEEE 829 §5.2)

### 2.1 Mục đích

Kế hoạch này xác định chiến lược, phạm vi, tiêu chí đạt/không đạt, môi trường, trách nhiệm và lịch kiểm thử cho MVP "Chat với tài liệu": người dùng tải PDF lên kho chung, hỏi bằng ngôn ngữ tự nhiên, nhận câu trả lời kèm nguồn (tài liệu, trang) hoặc thông báo "không tìm thấy". Kế hoạch gắn mọi ca kiểm thử với tiêu chí chấp nhận (`US-xxx-ACn`) và cổng phát hành (G1–G13, PRD §5.1).

### 2.2 Phạm vi

**Trong phạm vi**
- Chức năng của 11 user story (US-001…US-010, US-015) và 13 use case trong `docs/diagrams/use-case-diagram.drawio` (nguồn sự thật về phạm vi).
- Trường hợp biên EC-01…EC-16 (PRD §4.2).
- API REST theo `docs/04-design/openapi.yaml` (kiểm hợp đồng mọi phản hồi).
- Chất lượng AI ở mức có thể đo: G4 (nguồn đúng), G5 (ngoài tài liệu → "không tìm thấy"), ổn định giữa các lần chạy.
- Bảo mật: kiểm tra tệp tải lên, phân quyền CSDL tối thiểu, không lộ nội dung trong log, TLS + tiêu đề bảo mật ở proxy, quét bí mật.
- Vận hành: tắt êm/nâng cấp cuốn chiếu, xóa vật lý, đối soát kho ↔ CSDL, sao lưu/khôi phục.
- Khả năng tiếp cận và giao diện ở mức thành phần (vitest) và trình duyệt thật (Playwright + axe, S8-08 — đã lập kế hoạch).

**Ngoài phạm vi** — xem §5.

### 2.3 Mục tiêu

| Mã | Mục tiêu | Tiêu chí thành công | Truy vết |
|---|---|---|---|
| OBJ-01 | Xác nhận mọi AC của story P0 | 100% AC P0 có ca kiểm thử tự động đạt (trừ AC bị chặn bởi OQ) | G1, US-001…US-010 |
| OBJ-02 | Xác nhận hợp đồng API | 100% endpoint của `openapi.yaml` được gọi trong test tích hợp; mọi phản hồi khớp schema | API_Design.md |
| OBJ-03 | Xác nhận AI trung thực | G4 = 100%, G5 = 100% trên bộ đánh giá; G3 ≥ `[TBD: OQ-004]` | G3, G4, G5, BR-010/011 |
| OBJ-04 | Xác nhận bảo mật | 0 lỗ hổng cao/nghiêm trọng mở; 0 bí mật trong lịch sử git | G9, NFR-SEC-001/002 |
| OBJ-05 | Xác nhận khả năng tiếp cận | 0 vi phạm axe mức `serious`/`critical` (WCAG 2.1 AA) trên các màn hình chính | OQ-P02, S8-08 |
| OBJ-06 | Giữ chất lượng mã | Cổng L0 xanh; coverage ≥ 70%; rubric review ≥ 10/14 | Quy trình giai đoạn 7–8 |

### 2.4 Tài liệu tham chiếu

| Tài liệu | Đường dẫn | Vai trò trong kế hoạch |
|---|---|---|
| BRD v0.6 | `docs/02-requirements/BRD.md` | BR-xxx, rủi ro RSK-xxx |
| PRD v0.6 | `docs/03-analysis/PRD.md` | NFR, EC, cổng phát hành |
| User stories | `docs/03-analysis/USER_STORIES.md` | AC Given-When-Then |
| Ma trận truy vết | `docs/03-analysis/traceability.md` | BR ↔ US ↔ UC |
| SAD (IEEE 1016) | `docs/04-design/SAD.md` | Thành phần, luồng, ràng buộc chất lượng |
| Blueprint | `docs/04-design/Blueprint_Design.md` | Thiết kế chi tiết, G-L1/G-L2/G-L3 |
| API / OpenAPI | `docs/04-design/API_Design.md`, `openapi.yaml` | Hợp đồng API, 12 ProblemCode |
| CSDL | `docs/04-design/Database_Design.md`, `schema.sql` | Phân quyền, vòng đời tài liệu |
| Thiết kế màn hình | `docs/04-design/html_design/` | Trạng thái UI |
| Kế hoạch triển khai | `docs/05-implement/PLAN.md`, `tasks/` | Task S0…S8, tiêu chí hoàn thành |
| Cổng phát hành | `docs/05-implement/release-gates.md` | Bằng chứng G1–G13 |
| IEEE 829-2008 | — | Cấu trúc tài liệu |

### 2.5 Phân tích đầu vào (tóm tắt)

**Thành phần (SAD — khối module, ports & adapters):**

| Khung nhìn | Phần tử | Giao diện / trạng thái | Kiểm thử ở mức |
|---|---|---|---|
| Thành phần | `api` (FastAPI), `worker`, `core` (documents, ingestion, retrieval, answer, guard), `ports`, `adapters`, `persistence` | import-linter 3 hợp đồng (core không phụ thuộc adapter/hạ tầng) | L0 (lint-imports) |
| Thành phần–kết nối | API ↔ PostgreSQL (vai trò `cwd_api`), worker ↔ PostgreSQL (`cwd_worker`), ↔ kho đối tượng (IF-03), ↔ dịch vụ AI (IF-02) | Port: `ObjectStorePort`, `LlmPort`, `PdfExtractorPort` | Tích hợp, adapter |
| Tương tác | Tải lên → hàng đợi `jobs` → xử lý → `ready`; Hỏi → truy xuất lai → G-L1 → LLM → G-L2 → G-L3 | — | Tích hợp, E2E |
| Thông tin | `documents`, `chunks` (vector + tsv), `jobs` | Xóa mềm + purge | Tích hợp, phân quyền |
| Giao diện | 7 endpoint `/api/v1/*`, `/healthz`, `/readyz`, `/metrics` | problem+json (RFC 9457) | Hợp đồng |
| Động thái trạng thái | Tài liệu: `processing → ready \| failed`, `deleted_at`; Việc: `queued → running → done \| failed`, thử lại 30 s/120 s, tối đa 3 lần | — | Tích hợp (hàng đợi, bền vững) |

**Endpoint API:**

| Endpoint | Phương thức | Lỗi chính (ProblemCode) | Xác thực |
|---|---|---|---|
| `/api/v1/config` | GET | — | Không (CON-005) |
| `/api/v1/documents` | GET, POST | `FILE_TOO_LARGE`, `UNSUPPORTED_TYPE`, `INVALID_REQUEST`, `STORAGE_UNAVAILABLE`, `SYSTEM_BUSY`, `RATE_LIMITED` | Không |
| `/api/v1/documents/{id}` | GET, DELETE | `NOT_FOUND` | Không |
| `/api/v1/documents/{id}/file` | GET (Range, If-None-Match) | `NOT_FOUND`, 416 | Không |
| `/api/v1/questions` | POST | `EMPTY_QUESTION`, `QUESTION_TOO_LONG`, `AI_UNAVAILABLE`, `AI_TIMEOUT`, `SYSTEM_BUSY`, `RATE_LIMITED` | Không |

**Thành phần giao diện:** danh sách tài liệu (trạng thái sẵn sàng/đang xử lý/lỗi + lý do), vùng tải lên (kéo thả, tiến độ, hủy), khung hỏi đáp (trống/đang chờ/lỗi + đếm ngược Retry-After), chip nguồn (mở PDF đúng trang, "(đã xóa)"), hộp thoại xóa (focus vào Hủy, Esc đóng), bố cục điện thoại 390 px.

### 2.6 Đánh giá rủi ro sản phẩm (định hướng ưu tiên kiểm thử)

| Mã | Rủi ro | Khả năng (1–5) | Tác động (1–5) | Điểm | Giảm thiểu bằng kiểm thử |
|---|---|---|---|---|---|
| RSK-001 | Trả lời sai / bịa nội dung | 4 | 5 | **20** | G-L1/G-L2/G-L3 + bộ đánh giá G4/G5 + bộ câu hỏi ngoài phạm vi; chạy lại với AI thật |
| RSK-002 | Rò rỉ dữ liệu tài liệu | 3 | 5 | **15** | Test log không chứa nội dung; phân quyền CSDL; TLS/tiêu đề; quét bí mật; chặn worker ra Internet |
| RSK-P03 | Không đăng nhập — ai vào được đều xóa được | 3 | 4 | 12 | Allowlist mạng ở proxy (proxy-test); ghi rõ phạm vi ở §5 |
| RSK-005 | PDF không đọc được / độc hại | 4 | 3 | 12 | Trích xuất trong tiến trình con có hạn thời gian/bộ nhớ; ca PDF hỏng/mật khẩu/ảnh quét |
| RSK-P02 | Chậm → người dùng bỏ | 3 | 3 | 9 | Spike HNSW; LoadGuard/429; đo thời gian sẵn sàng (NFR-PRF-002, chờ OQ-P07) |
| R-OPS | Mất/nhân đôi việc khi worker chết | 2 | 4 | 8 | Test hàng đợi đồng thời, `release_overdue`, đối soát |
| R-DEL | Tài liệu đã xóa vẫn xuất hiện trong câu trả lời | 2 | 5 | 10 | Test xóa tức thì + đua giữa truy xuất và xóa (G-L3 lọc lại) |

## 3. Đối tượng kiểm thử (IEEE 829 §5.3)

| Mã | Đối tượng | Phiên bản | Vị trí | Hình thức |
|---|---|---|---|---|
| SI-01 | Máy chủ API (`cwd_server.api`) | `ec18ff6`+ | `app/server/cwd_server/api/` | Dịch vụ REST (uvicorn) |
| SI-02 | Worker (`cwd_server.worker`) — xử lý, purge, quét, đối soát | `ec18ff6`+ | `app/server/cwd_server/worker/` | Tiến trình nền |
| SI-03 | Lõi nghiệp vụ (`core/*`) | `ec18ff6`+ | `app/server/cwd_server/core/` | Thư viện |
| SI-04 | Adapter: kho tệp cục bộ, S3, PyMuPDF, LLM HTTP, LLM giả, bọc chịu lỗi | `ec18ff6`+ | `app/server/cwd_server/adapters/` | Thư viện |
| SI-05 | Ứng dụng web (React SPA) | `ec18ff6`+ | `app/web/src/` | Gói tĩnh `dist/` |
| SI-06 | Lược đồ CSDL + migration + vai trò | `schema.sql` / Alembic | `docs/04-design/schema.sql`, `persistence/migrations/` | PostgreSQL 17 + pgvector |
| SI-07 | Cấu hình triển khai: compose, Dockerfile, nginx | `ec18ff6`+ | `app/deploy/` | Ảnh `cwd-server`, `cwd-web` |
| SI-08 | Bộ đánh giá chất lượng AI | `synthetic.jsonl` (15 câu) | `app/server/eval_cwd/` | Script |

**Hiện vật kiểm thử đi kèm**

| Mã | Hiện vật | Định dạng | Vị trí |
|---|---|---|---|
| TA-01 | Test đơn vị server (48) | pytest | `app/server/tests/unit/` |
| TA-02 | Test tích hợp server (29) — PostgreSQL thật, kiểm hợp đồng OpenAPI | pytest | `app/server/tests/integration/` |
| TA-03 | Test thành phần web (8) | vitest + Testing Library | `app/web/src/app/app.test.tsx` |
| TA-04 | Kiểm tra khói đầu-cuối (17 bước) | Python/httpx | `app/server/scripts/smoke.py` |
| TA-05 | Kiểm tra proxy (13) và nâng cấp cuốn chiếu (7) | bash | `app/deploy/proxy/proxy-test.sh`, `deploy/prod-local/rolling-test.sh` |
| TA-06 | Dữ liệu thử: 5 PDF minh họa (hợp đồng, báo giá, quy định, có mật khẩu, không phải PDF) | PDF sinh bằng script | `app/server/scripts/make_samples.py` → `app/samples/` |
| TA-07 | Giả lập: `FakeLlm` (kịch bản, chèn lỗi), `ExtractiveLlm` (demo), `InMemoryObjectStore` (chèn lỗi) | Python | `adapters/llm_local.py`, `adapters/stores.py` |
| TA-08 | Truy vết AC → test (`@pytest.mark.req`, `[US-xxx-ACn]` trong tên test web) | script | `app/server/scripts/trace_check.py` (`make trace`) |
| TA-09 | Workflow CI L0 | GitHub Actions | `.github/workflows/ci.yml`; bản cục bộ `make ci` |

## 4. Tính năng được kiểm thử (IEEE 829 §5.4)

### 4.1 Ma trận ưu tiên

Điểm rủi ro = khả năng × tác động (§2.6) quy về thang 100; ưu tiên Cao ≥ 60.

| Ưu tiên | Tính năng | Story | BR | Điểm |
|---|---|---|---|---|
| **Cao** | F-06 Từ chối khi thiếu căn cứ | US-010 | BR-010 | 100 |
| **Cao** | F-05 Hỏi đáp có trích dẫn nguồn | US-006, US-007 | BR-006, BR-007 | 100 |
| **Cao** | F-07 Tổng hợp nhiều tài liệu | US-009 | BR-009 | 80 |
| **Cao** | F-04 Xóa tài liệu (khỏi mọi câu trả lời sau) | US-005 | BR-004 | 75 |
| **Cao** | F-01 Tải PDF + kiểm tra tệp | US-001 | BR-001, BR-005 | 60 |
| **Cao** | F-02 Trạng thái xử lý + lý do lỗi | US-002, US-003 | BR-002, BR-018 | 60 |
| Trung bình | F-08 Số trang của nguồn | US-008 | BR-008 | 50 |
| Trung bình | F-09 Chịu tải: bận/giới hạn tốc độ, AI lỗi | — (EC-07, EC-15, NFR-SCL-002) | BR-006 | 45 |
| Trung bình | F-10 Vận hành: purge, đối soát, nâng cấp cuốn chiếu | — (G11) | BR-004 | 40 |
| Thấp | F-03 Danh sách tài liệu | US-004 | BR-003 | 30 |
| Bị chặn | F-11 Vị trí lưu trữ | US-015 | BR-016 | — (OQ-005) |

### 4.2 Ma trận tính năng × loại kiểm thử

| Tính năng | Đơn vị | Tích hợp | Hệ thống/E2E | Chấp nhận | Hồi quy | Hiệu năng | Bảo mật | Tiếp cận | Chất lượng AI |
|---|---|---|---|---|---|---|---|---|---|
| F-01 Tải PDF | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (tệp 23 MB, nâng cấp cuốn chiếu) | ✓ | ✓ | — |
| F-02 Trạng thái | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | — |
| F-03 Danh sách | — | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | — |
| F-04 Xóa | — | ✓ | ✓ | ✓ | ✓ | — | ✓ (purge, phiên bản S3) | ✓ | ✓ |
| F-05 Hỏi + nguồn | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (spike truy xuất) | ✓ (prompt injection) | ✓ | ✓ |
| F-06 Không tìm thấy | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ |
| F-07 Nhiều tài liệu | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | — | ✓ |
| F-08 Trang | — | ✓ | ✓ | ✓ | ✓ | — | — | — | ✓ |
| F-09 Chịu tải | ✓ | ✓ | — | — | ✓ | ✓ | ✓ (giới hạn tốc độ) | ✓ (thông báo lỗi) | — |
| F-10 Vận hành | — | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | — |

### 4.3 Mô tả tính năng và AC

| Tính năng | Ca kiểm thử cần chứng minh | AC / EC |
|---|---|---|
| F-01 | PDF hợp lệ được nhận; đúng giới hạn thì nhận, hơn 1 byte thì từ chối; tệp không phải PDF (đuôi, magic bytes, rỗng) bị từ chối; tải lên nguyên tử khi kho hoặc CSDL lỗi | US-001-AC1…AC3, EC-02, EC-03, EC-06 |
| F-02 | `processing → ready`; PDF hỏng / có mật khẩu / ảnh quét → `failed` + lý do; câu hỏi không dùng tài liệu chưa sẵn sàng | US-002-AC1/AC2, US-003-AC1…AC4, EC-04, EC-05 |
| F-03 | Danh sách đủ tên + trạng thái, mới nhất trước | US-004-AC1 |
| F-04 | Xóa → biến mất ngay khỏi danh sách và mọi câu trả lời sau; purge xóa tệp trước rồi mới xóa bản ghi; nguồn cũ hiển thị "(đã xóa)" | US-005-AC1/AC2, EC-16 |
| F-05 | Trả lời có nguồn đúng tài liệu; mã trích dẫn chỉ thuộc tập đã gửi (G-L2); tên + trang lấy từ CSDL (G-L3); trả lời cùng ngôn ngữ | US-006-AC1…AC3, US-007-AC1/AC2, EC-01, EC-08, EC-09 |
| F-06 | Câu ngoài tài liệu → "không tìm thấy", không bịa; trả lời một phần nêu phần thiếu | US-010-AC1/AC2, EC-10 |
| F-07 | Nguồn đủ N tài liệu, không thừa; mâu thuẫn được nêu rõ | US-009-AC1/AC2, EC-11 |
| F-08 | Số trang khớp mẫu | US-008-AC1 |
| F-09 | 503 `SYSTEM_BUSY` khi quá tải, tài liệu không mất; 429 có `Retry-After`; lỗi AI → giữ câu hỏi, cho gửi lại | NFR-SCL-002, EC-07, EC-15 |
| F-10 | Nâng cấp cuốn chiếu không cắt tải giữa chừng; đối soát dọn tệp mồ côi; sao lưu/khôi phục | G11 |

## 5. Tính năng không được kiểm thử (IEEE 829 §5.5)

| Tính năng | Lý do | Rủi ro | Kế hoạch |
|---|---|---|---|
| Đăng nhập / phân quyền người dùng | Không có trong MVP (CON-005, ASM-004) | Trung bình (RSK-P03) | Thay bằng allowlist mạng; bổ sung khi mở rộng |
| Độ đúng nội dung câu trả lời với mô hình thật (G3) | Chưa có ngưỡng (OQ-004), bộ câu hỏi thật (DEP-002) và quyết định dùng AI bên ngoài (OQ-005) | **Cao** | `make eval` sinh CSV cho người chấm; chạy lại khi OQ đóng |
| Vị trí lưu trữ (US-015, G8) | Chờ chính sách OQ-005 | Cao (tuân thủ) | Rà soát cấu hình với CNTT/Pháp lý |
| Tải đồng thời ở quy mô mục tiêu (NFR-SCL-001) | Số người dùng chưa có (OQ-001) | Trung bình | Kịch bản k6 khi có số liệu |
| Thời gian sẵn sàng tối đa (NFR-PRF-002) | Ngưỡng chưa có (OQ-P07) | Thấp | Đo `durationMs` từ log `document_ready` |
| Ma trận trình duyệt | Danh sách chưa có (OQ-P09) | Thấp | Chromium (Playwright) làm mặc định |
| Tài liệu trùng tên/nội dung (EC-12) | Hành vi chưa quyết định (OQ-014) | Thấp | Hệ thống hiện giữ cả hai |
| Thời gian hoạt động của dịch vụ AI bên thứ ba | Trách nhiệm nhà cung cấp | Thấp | Đã kiểm hành vi khi AI lỗi (breaker, retry) |
| Kiểm thử xâm nhập chuyên sâu | Cần đội bảo mật | Trung bình | Đề xuất trước khi mở cho người dùng ngoài nhóm thử |
| Mã hóa lúc lưu trữ (NFR-SEC-002) | Do hạ tầng cung cấp, chờ OQ-P08 | Cao (tuân thủ) | Rà soát cấu hình nền tảng |

## 6. Cách tiếp cận (IEEE 829 §5.6)

### 6.1 Tháp đảm bảo chất lượng

| Tầng | Ai | Làm gì | Công cụ | Chặn merge? |
|---|---|---|---|---|
| **L0 — Máy** | CI | lint, kiểu, hợp đồng phụ thuộc, test (đơn vị + tích hợp), coverage ≥ 70%, quét bí mật, build < 10 phút | `.github/workflows/ci.yml` (cục bộ: `make ci`) | **Có** |
| **L1 — Agent** | Agent review | Review diff theo rubric 7 tiêu chí + checklist IEEE 1028, trích dẫn dòng; **không có quyền approve/merge/deploy** | `review-record.md` | Không (chỉ khuyến nghị) |
| **L2 — Người** | 1 approver ≠ tác giả | Đọc diff (không đọc tóm tắt), chấm rubric, PR ≤ 400 dòng; merge khi ≥ 10/14 và L0 xanh | Pull request | **Có** |
| **L3 — Inspection** | Người review + chuyên gia | Inspection IEEE 1028 cho diff rủi ro cao: tải tệp/trích PDF, xóa/purge, dữ liệu gửi ra AI, phân quyền CSDL, proxy | Biên bản inspection | **Có** cho diff thuộc nhóm này |
| **L4 — Xác nhận với stakeholder** | Business owner | Demo + UAT với người dùng thật (G12), chấm G3 | Biên bản UAT | Chặn phát hành |

### 6.2 Tự động và thủ công

| Hoạt động | Tự động (CI / make) | Thủ công |
|---|---|---|
| Đơn vị, tích hợp, hợp đồng API, coverage | ✓ mỗi PR | — |
| Lint, kiểu (mypy, tsc), import-linter, quét bí mật, build ảnh | ✓ mỗi PR | — |
| Khói đầu-cuối (`make smoke`) | ✓ trên hệ thống đang chạy | — |
| Proxy, nâng cấp cuốn chiếu (`make proxy-test`, `rolling-test.sh`) | ✓ trên stack `prod-up` (Docker) | — |
| E2E trình duyệt + axe (S8-08) | ✓ (kế hoạch) | — |
| Đánh giá AI (`make eval`) | ✓ chỉ số G4/G5 | Chấm độ đúng G3 (CSV) |
| Khám phá trên trình duyệt, đọc màn hình (VoiceOver/NVDA) | — | ✓ mỗi vòng phát hành |
| UAT, đếm số thao tác (G12) | — | ✓ business owner |
| Review mã L2, inspection L3 | — | ✓ |

### 6.3 Kiểm thử đơn vị

| Thuộc tính | Mô tả |
|---|---|
| Phụ trách | Tác giả mã |
| Công cụ | pytest (server), vitest + Testing Library (web) |
| Coverage | ≥ 70% (tổng câu lệnh + nhánh, coverage.py; dòng/nhánh/hàm, v8) — cổng CI |
| Đầu vào | Mã biên dịch được, lint sạch |
| Đầu ra | 100% test đạt, coverage đạt ngưỡng |
| Trọng tâm | Kiểm tra tệp tải lên, chia đoạn, RRF, tsquery an toàn, lời nhắc + G-L2, giới hạn tốc độ, LoadGuard, breaker, adapter LLM/PDF |
| Giả lập | `FakeLlm`, `InMemoryObjectStore`, đồng hồ giả |

### 6.4 Kiểm thử tích hợp và API

| Thuộc tính | Mô tả |
|---|---|
| Phụ trách | Tác giả mã; QA rà soát |
| Công cụ | pytest + FastAPI TestClient trên PostgreSQL 17 + pgvector thật; `tests/support/openapi_assert.py` kiểm mọi phản hồi theo `openapi.yaml` |
| Phạm vi | 7 endpoint; hàng đợi `SKIP LOCKED` đồng thời; phân quyền vai trò `cwd_api`/`cwd_worker`; adapter S3 (SeaweedFS) |
| Đầu vào | Đơn vị đạt; CSDL `cwd_test` sẵn sàng |
| Đầu ra | 100% đạt |

**Ca API chính (ánh xạ tới test thật):**

| Mã | Endpoint | Loại | Kiểm tra | Test |
|---|---|---|---|---|
| API-01 | `POST /documents` | Dương | 202, `Location`, trạng thái `processing` | `test_upload_list_get` |
| API-02 | `POST /documents` | Âm | 413 `FILE_TOO_LARGE` (biên +1 byte), 415 `UNSUPPORTED_TYPE`, 400 thiếu tệp | `test_upload_rejections`, `test_upload_exact_limit_ok_one_byte_over_rejected` |
| API-03 | `POST /documents` | Nguyên tử | Kho lỗi / CSDL lỗi ⇒ không có dòng, không có tệp mồ côi | `test_upload_atomic_on_failures` |
| API-04 | `GET /documents` | Dương | Danh sách, thứ tự, trạng thái | `test_upload_list_get` |
| API-05 | `GET /documents/{id}/file` | Dương/Âm | 200, 206 Range, 304 ETag, 416, 404 | `test_file_endpoint` |
| API-06 | `DELETE /documents/{id}` | Bất biến | 204, xóa lần 2 vẫn 204, id lạ 404 | `test_delete_is_immediate_everywhere` |
| API-07 | `POST /questions` | Dương | `answered` + nguồn từ CSDL | `test_ask_answered_with_sources` |
| API-08 | `POST /questions` | Âm | `EMPTY_QUESTION`, `QUESTION_TOO_LONG` | `test_question_validation` |
| API-09 | `POST /questions` | Lỗi phụ thuộc | `AI_UNAVAILABLE`/`AI_TIMEOUT` + `Retry-After` | `test_ai_errors_mapped` |
| API-10 | mọi endpoint | Chịu tải | 503 `SYSTEM_BUSY`, 429 `RATE_LIMITED` | `test_busy_and_rate_limit` |
| API-11 | `/readyz` | Phân quyền | Đạt khi chạy bằng vai trò tối thiểu | `test_readyz_queries_work_under_least_privilege` |

### 6.5 Kiểm thử hệ thống / đầu-cuối

| Thuộc tính | Mô tả |
|---|---|
| Phụ trách | QA |
| Công cụ | `scripts/smoke.py` (HTTP); Playwright + axe-core trên Chromium (S8-08) |
| Đầu vào | Tích hợp đạt; hệ thống chạy (`make demo` hoặc `make prod-up`) |
| Đầu ra | 100% bước đạt; 0 lỗi nghiêm trọng mở |

| Mã | Hành trình | Bước | Kết quả mong đợi |
|---|---|---|---|
| E2E-01 | Tải → sẵn sàng → hỏi | Tải `hop-dong-A.pdf`, chờ `ready`, hỏi điều khoản thanh toán | Trả lời có nguồn `hop-dong-A.pdf` trang 1; chip mở PDF đúng trang |
| E2E-02 | Nhiều tài liệu | Tải thêm B, C; hỏi so sánh thời hạn thanh toán | Nguồn liệt kê A và B |
| E2E-03 | Ngoài tài liệu | Hỏi câu không có trong tài liệu | "Không tìm thấy…", không có nguồn |
| E2E-04 | Lỗi tệp | Tải PDF có mật khẩu, tệp `.txt` | Lý do lỗi + hướng xử lý; `.txt` không tạo dòng |
| E2E-05 | Xóa | Xóa C, hỏi lại câu về C | Không còn nguồn C; nguồn cũ hiển thị "(đã xóa)" |
| E2E-06 | Qua proxy TLS | Lặp E2E-01…05 qua `https://localhost:8443` | Như trên + tiêu đề bảo mật |
| E2E-07 | Điện thoại | Mở ở 390 px | Không cuộn ngang; thao tác chính dùng được |

### 6.6 Kiểm thử chấp nhận (UAT — L4)

| Thuộc tính | Mô tả |
|---|---|
| Phụ trách | Business owner + người dùng thật (nhân viên phát triển kinh doanh, trưởng nhóm) |
| Công cụ | Kịch bản UAT, biên bản; bộ tài liệu thật DEP-002 |
| Đầu vào | Kiểm thử hệ thống đạt; G4, G5 đạt; OQ-005 đóng nếu dùng tài liệu thật |
| Đầu ra | Ký G12; chấm G3 đạt ngưỡng OQ-004 |

| Mã | Story | Kịch bản | Tiêu chí |
|---|---|---|---|
| UAT-01 | US-001…003 | Người dùng tự tải 5 tài liệu thật, gồm 1 tệp lỗi | Hiểu được trạng thái và lý do lỗi không cần hướng dẫn |
| UAT-02 | US-006, US-007 | 20 câu hỏi thật thuộc bộ DEP-002 | G3 ≥ `[TBD: OQ-004]`; 100% câu có nội dung có nguồn đúng |
| UAT-03 | US-010 | 10 câu ngoài tài liệu do người dùng tự đặt | 100% "không tìm thấy" |
| UAT-04 | US-009 | 5 câu cần ghép ≥ 2 tài liệu | Có đủ nguồn; nêu mâu thuẫn nếu có |
| UAT-05 | Trụ cột P3 | Đếm số thao tác so với cách thủ công | Business owner xác nhận cải thiện |

### 6.7 Kiểm thử hồi quy

| Bộ | Phạm vi | Số ca | Thời gian | Tự động |
|---|---|---|---|---|
| REG-01 | Đơn vị server + web | 48 + 8 | < 10 s | ✓ CI |
| REG-02 | Tích hợp + hợp đồng API | 29 | ~ 20 s | ✓ CI |
| REG-03 | Khói đầu-cuối | 17 bước | ~ 30 s | ✓ `make smoke` |
| REG-04 | Proxy + cuốn chiếu | 13 + 7 | ~ 2 phút | ✓ `make proxy-test` |
| REG-05 | Đánh giá AI G4/G5 | 15 câu | ~ 10 s | ✓ `make eval` |

Kích hoạt: mỗi PR (REG-01, 02); trước mỗi bản phát hành và sau mỗi thay đổi ở ingestion/retrieval/answer (REG-03…05). **Mọi lỗi tìm được phải có ca hồi quy** (ví dụ q15 trong REG-05 cho DEF-001).

### 6.8 Kiểm thử hiệu năng

| Mã | Loại | Tải | Chỉ số | Ngưỡng | Trạng thái |
|---|---|---|---|---|---|
| PERF-01 | Truy xuất | 40.000 đoạn / 384 chiều | p95 truy vấn vector | Đề xuất ≤ 100 ms | Đã chạy (spike S3-00: 27 ms) |
| PERF-02 | Tải tệp lớn khi nâng cấp | 23 MB, dừng 1 bản API giữa chừng | Không cắt kết nối | 0 lỗi | Đã chạy (rolling 7/7) |
| PERF-03 | Đồng thời | `[TBD: OQ-001]` người dùng | 0 lỗi do quá tải; 503 có `Retry-After` khi vượt | NFR-SCL-001/002 | Chờ OQ-001 |
| PERF-04 | Thời gian sẵn sàng | Tài liệu điển hình | `durationMs` của `document_ready` | `[TBD: OQ-P07]` | Chờ OQ-P07 |
| PERF-05 | Build CI | — | Tổng thời gian L0 | < 10 phút | Đo mỗi lần CI |

### 6.9 Kiểm thử bảo mật

| Mã | Kiểm tra | Cách | Mong đợi |
|---|---|---|---|
| SEC-01 | Tệp tải lên không tin cậy | Magic bytes, giới hạn kích thước, làm sạch tên; trích PDF trong tiến trình con có hạn thời gian/bộ nhớ | Từ chối/đánh dấu lỗi, không treo worker |
| SEC-02 | Injection | SQL tham số hóa; tsquery chỉ ghép từ chữ/số; khối tài liệu đánh dấu "là dữ liệu" trong lời nhắc | `test_tsquery_safe`, `test_prompt_marks_data_block` |
| SEC-03 | Phân quyền CSDL tối thiểu | Chạy truy vấn thật bằng `cwd_api`/`cwd_worker` | Thao tác cấm bị từ chối |
| SEC-04 | Không lộ nội dung | Log chỉ có trường cho phép; lỗi trả problem+json không chi tiết nội bộ | `test_observability_no_content_leak` |
| SEC-05 | Truyền tải | TLS ≥ 1.2, HSTS, CSP, nosniff, no-referrer, `server_tokens off` | `make proxy-test` |
| SEC-06 | Kiểm soát truy cập mạng | Allowlist dải nội bộ; `/metrics` chỉ 10/8 | 403 ngoài allowlist |
| SEC-07 | Bí mật | gitleaks toàn bộ lịch sử git; bí mật chỉ ở tệp bị gitignore | 0 phát hiện |
| SEC-08 | Container | Không root, `read_only`, `no-new-privileges`, worker không ra Internet | Kiểm bằng `docker inspect` (S8-05) |
| SEC-09 | Lạm dụng tài nguyên | Giới hạn tốc độ, LoadGuard, giới hạn kích thước thân yêu cầu | 429/503/413 |
| SEC-10 | Quét lỗ hổng phụ thuộc + ảnh | `pip-audit`, `npm audit`, quét ảnh | 0 mức cao/nghiêm trọng (G9) — **chưa chạy** |

### 6.10 Kiểm thử khả năng tiếp cận (WCAG 2.1 AA)

| Mã | Kiểm tra | Mô tả | Mong đợi |
|---|---|---|---|
| ACC-01 | Bàn phím | Tab qua toàn bộ điều khiển; liên kết "Bỏ qua tới khung hỏi đáp" | Dùng được không cần chuột |
| ACC-02 | Đọc màn hình | VoiceOver: trạng thái tài liệu, câu trả lời mới, lỗi | Được đọc (vùng `aria-live`, `role=alert`) |
| ACC-03 | Tương phản | axe `color-contrast` | ≥ 4.5:1 |
| ACC-04 | ARIA | axe toàn trang ở các trạng thái: trống, có tài liệu, có câu trả lời, hộp thoại mở | 0 `serious`/`critical` |
| ACC-05 | Focus | Hộp thoại xóa: focus vào Hủy, Esc đóng, trả focus về nút mở | Test thành phần (đã có) + Playwright |
| ACC-06 | Thông báo lỗi | Lỗi tải/hỏi có chữ, không chỉ màu | Test thành phần (đã có) |

### 6.11 Kiểm thử giao diện

| Mã | Kiểm tra | Mong đợi |
|---|---|---|
| UI-01 | So với `html_design/` | Bố cục và chữ trên nút khớp; khác biệt được ghi lại |
| UI-02 | Đáp ứng 320–1440 px | Không cuộn ngang |
| UI-03 | Trạng thái thành phần | Trống, đang tải (tiến độ), đang xử lý, sẵn sàng, lỗi, đang chờ trả lời, lỗi AI có đếm ngược |
| UI-04 | Lỗi | Bảng ánh xạ `uiErrors.ts`: mã lạ ⇒ lỗi chung có mã tham chiếu |

### 6.12 Đánh giá chất lượng AI

| Chỉ số | Định nghĩa | Ngưỡng | Công cụ |
|---|---|---|---|
| G4 | Câu có trả lời mà mọi nguồn đúng tài liệu kỳ vọng | 100% | `make eval` |
| G5 | Câu ngoài tài liệu trả `not_found` | 100% | `make eval` |
| Ổn định | Cùng câu hỏi, 2 lần chạy cùng kết quả | 100% | `make eval` |
| G3 | Câu trả lời đúng nội dung theo người chấm | `[TBD: OQ-004]` (đề xuất ≥ 85%) | CSV chấm tay |

Lưu ý: bộ `synthetic.jsonl` nhỏ và đã được dùng để chỉnh AI giả, nên có thiên lệch. Bộ thật DEP-002 phải được giữ riêng (không dùng để chỉnh).

## 7. Tiêu chí đạt/không đạt (IEEE 829 §5.7)

| Mức | Đạt khi |
|---|---|
| Ca kiểm thử | Kết quả thực tế khớp mong đợi; test tự động trả 0 |
| PR (L0) | 10/10 bước `make ci` / workflow xanh; coverage ≥ 70%; 0 bí mật; build < 10 phút |
| PR (L1/L2) | Không còn phát hiện mức **Major** chưa xử lý; rubric ≥ **10/14**, không tiêu chí nào 0 điểm ở An toàn hoặc Đúng AC |
| Story | Mọi AC có ca kiểm thử đạt |
| Bản phát hành | Mọi cổng **Must** đạt: G1 (100% AC P0), G2 (0 lỗi nghiêm trọng/chặn mở với P0), G3 (≥ OQ-004), G4 = 100%, G5 = 100%, G8, G9 (0 lỗ hổng cao/nghiêm trọng), G12, G13 |

**Phân loại mức nghiêm trọng của lỗi**

| Mức | Định nghĩa | Ví dụ |
|---|---|---|
| Chặn (Blocker) | Không dùng được luồng chính, mất dữ liệu, lộ dữ liệu | Tài liệu đã xóa vẫn xuất hiện trong câu trả lời |
| Nghiêm trọng (Major) | Vi phạm AC P0 hoặc cổng Must; có cách tránh | Câu ngoài tài liệu nhận câu trả lời "có căn cứ" (vi phạm G5) |
| Nhỏ (Minor) | Sai lệch không ảnh hưởng AC P0 | Thiếu tiêu đề `X-Request-Id` ở một mã lỗi |
| Góp ý | Cải thiện chất lượng mã/UX | Thông báo "sẵn sàng" không tự ẩn |

## 8. Tiêu chí tạm dừng và tiếp tục (IEEE 829 §5.8)

**Tạm dừng toàn bộ chu kỳ khi:**
1. Môi trường thử hỏng lặp lại: CSDL thử mất kết nối > 3 lần trong một lượt, hoặc CI đỏ vì hạ tầng (không phải vì mã) hai lần liên tiếp.
2. Phát hiện lỗi mức **Chặn** ở luồng tải lên hoặc hỏi đáp (mọi ca phía sau sẽ cho kết quả vô nghĩa).
3. Phát hiện rò rỉ dữ liệu hoặc bí mật (SEC-04, SEC-07) — dừng ngay, kích hoạt quy trình "Xóa khẩn cấp" trong `runbook.md`.
4. Bản build được kiểm không khớp commit đã khai báo.

**Tiếp tục khi:**
1. Bản sửa đã merge qua L0 + L2, và có ca hồi quy cho lỗi đó.
2. Môi trường được dựng lại từ đầu (`make db-down && make db-up` / `make prod-down && make prod-up`), dữ liệu thử sinh lại (`make samples`).
3. Chạy lại REG-01…REG-03 đạt trước khi tiếp tục các ca còn lại.
4. Với sự cố rò rỉ: CNTT/bảo mật xác nhận đã xử lý (OQ-005).

## 9. Sản phẩm bàn giao của kiểm thử (IEEE 829 §5.9)

Lưu tại `docs/07-verification/` (và đính kèm vào PR/work item):

| Sản phẩm | Tệp | Tạo bởi |
|---|---|---|
| Kế hoạch kiểm thử (tài liệu này) + checklist IEEE 829 đã điền | `test-plan.md`, `Test_Plan_IEEE_829_Checklist.xlsx` | Agent soạn, QA Lead duyệt |
| Báo cáo kiểm thử (Test Summary Report) | `test-report.md` | Agent / QA |
| Log CI | `evidence/ci.log` (cục bộ), artifact `server-reports` (GitHub Actions) | CI |
| Báo cáo coverage | `evidence/coverage-summary.md`, `evidence/server-coverage.xml`, `evidence/web-coverage-summary.json` | CI |
| Log khói, proxy, đánh giá AI | `evidence/smoke.log`, `evidence/proxy-test.log`, `evidence/eval-report.md` | make |
| Biên bản review mã + checklist IEEE 1028 đã điền | `review-record.md`, `Code_Review_IEEE_1028_Checklist.xlsx` | Agent (L1), người review (L2/L3) |
| Mô tả PR + phê duyệt | `pr-description.md` → PR trên GitHub | Tác giả tạo PR; approver ≠ tác giả |
| Biên bản UAT | `uat-record.md` (chưa có) | Business owner |

## 10. Công việc kiểm thử (IEEE 829 §5.10)

| # | Công việc | Phụ trách | Phụ thuộc | Trạng thái |
|---|---|---|---|---|
| T1 | Lập và duyệt kế hoạch này | Agent → QA Lead | — | Đã soạn, chờ duyệt |
| T2 | Dựng CI L0 (workflow + `make ci`) | Agent | — | Xong |
| T3 | Bổ sung kiểm kiểu Python (mypy) và sửa lỗi | Agent | T2 | Xong (8 lỗi đã sửa) |
| T4 | Chạy REG-01…REG-05, thu bằng chứng | Agent | T2 | Xong |
| T5 | Review L1 theo rubric + IEEE 1028 | Agent | T4 | Xong |
| T6 | Mở PR, review L2 (approver ≠ tác giả), merge | Tác giả + approver | T5 | **Chờ người** |
| T7 | Bật bảo vệ nhánh `main` (bắt buộc CI + 1 approval) | Chủ repo | T2 | **Chờ người** |
| T8 | Sửa phát hiện Major (DEF-001, F-02, F-03) + ca hồi quy | Dev | T5 | Chưa làm |
| T9 | E2E trình duyệt + axe (S8-08) | Dev/QA | — | Chưa làm |
| T10 | Quét lỗ hổng phụ thuộc + ảnh (SEC-10) | Dev/QA | — | Chưa làm |
| T11 | Inspection L3 cho các vùng rủi ro cao | Người review + bảo mật | T6 | Chưa làm |
| T12 | Đánh giá G3 với AI thật + bộ DEP-002 | Business owner + QA | OQ-004, OQ-005 | Bị chặn |
| T13 | UAT (G12) | Business owner | T8–T12 | Bị chặn |

## 11. Nhu cầu môi trường (IEEE 829 §5.11)

| Môi trường | Thành phần | Dùng cho |
|---|---|---|
| Máy dev (macOS arm64) | Python 3.12, Node 22, PostgreSQL 17 + pgvector (Homebrew), kho tệp cục bộ | Đơn vị, tích hợp, khói, eval |
| Stack Docker dev (Colima) | `pgvector/pgvector:pg17` (cổng 5433), SeaweedFS 4.50 S3 (cổng 9000) | Tích hợp adapter S3 |
| Stack kiểu sản xuất (Colima) | api×2, worker, migrate, nginx-unprivileged TLS (8443), PostgreSQL có vai trò tối thiểu, S3 có versioning | Proxy, cuốn chiếu, bảo mật container |
| CI | GitHub Actions `ubuntu-24.04`, dịch vụ `pgvector/pgvector:pg17`, Python 3.12, Node 22, gitleaks 8.30.1, Docker | L0 |
| Trình duyệt | Chromium (Playwright), cửa sổ 1280×820 và 390×844 | E2E, axe, ảnh chụp |
| Dữ liệu thử | 5 PDF sinh bằng `make samples`; PDF 23 MB cho thử tải lớn; `synthetic.jsonl` | Mọi mức |
| Giả lập AI | `FakeLlm` (test), `ExtractiveLlm` (demo, không cần mạng) | Không gửi dữ liệu ra ngoài khi OQ-005 chưa đóng |
| UAT | Môi trường được CNTT duyệt (OQ-005), dữ liệu thật DEP-002 | G3, G12 |

## 12. Trách nhiệm (IEEE 829 §5.12)

| Vai trò | Người | Trách nhiệm |
|---|---|---|
| Tác giả mã | Dev (agent hỗ trợ) | Viết test đơn vị/tích hợp cùng mã; giữ L0 xanh; mở PR ≤ 400 dòng |
| Agent review (L1) | Claude | Review theo rubric, trích dòng; **không approve, merge hay deploy** |
| Approver (L2) | `[TBD: OQ-007]` — phải khác tác giả | Đọc diff, chấm rubric, quyết định merge |
| QA Lead | `[TBD: OQ-007]` | Duyệt kế hoạch; quản lý dữ liệu thử và bộ đánh giá; theo dõi lỗi (G2) |
| CNTT / Bảo mật | `[TBD: OQ-007]` | OQ-005, OQ-P08; inspection L3 phần bảo mật; G8, G9 |
| Business owner | `[TBD: OQ-007]` | Bộ câu hỏi DEP-002, chấm G3, UAT G12, ngoại lệ cho cổng Should |

## 13. Nhân lực và đào tạo (IEEE 829 §5.13)

| Nhu cầu | Ai | Cách đáp ứng |
|---|---|---|
| Hiểu cơ chế RAG và 3 lớp grounding (G-L1/2/3) để thiết kế ca ngoài phạm vi | QA, approver | Đọc Blueprint §3.5; xem DEF-001 làm ví dụ |
| Chấm câu trả lời nhất quán (G3) | Người chấm nghiệp vụ | Hướng dẫn chấm 3 mức + hiệu chỉnh trên 5 câu mẫu trước khi chấm |
| PostgreSQL/pgvector, hàng đợi `SKIP LOCKED` | Approver phần persistence | `Database_Design.md` §3–§5 |
| WCAG 2.1 AA, VoiceOver | QA | Hướng dẫn nội bộ `[TBD]` |
| Tiếng Việt có dấu trong tìm kiếm (bỏ dấu làm sai nghĩa) | Dev, QA | DEF-001 |

## 14. Lịch (IEEE 829 §5.14)

Ngày cụ thể phụ thuộc ngân sách/thời hạn MVP `[TBD: OQ-003]`; lịch theo mốc tương đối:

| Mốc | Nội dung | Điều kiện vào | Điều kiện ra |
|---|---|---|---|
| M1 — Xác minh (giai đoạn 7) | T1–T5 | Mã hoàn thành S0–S8 | L0 xanh, review L1 xong — **đạt 2026-10-28** |
| M2 — Review (giai đoạn 8) | T6, T7, T11 | M1 | PR được approve ≥ 10/14; inspection L3 xong |
| M3 — Sửa lỗi Major | T8 | M2 | 0 Major mở; G5 = 100% |
| M4 — Hệ thống đầy đủ | T9, T10 | M3 | E2E + axe đạt; 0 lỗ hổng cao |
| M5 — Chấp nhận | T12, T13 | OQ-004, OQ-005 đóng; M4 | G3, G8, G12 ký |

## 15. Rủi ro và phương án dự phòng (IEEE 829 §5.15)

| Rủi ro kiểm thử | Ảnh hưởng | Dự phòng |
|---|---|---|
| OQ-004/OQ-005 chưa đóng | Không đánh giá được G3, G8; không dùng được AI thật | Dùng `ExtractiveLlm` cục bộ cho mọi kiểm thử chức năng; tách G3/G8 thành cổng riêng |
| Bộ đánh giá nhỏ, đã dùng để chỉnh | Báo đạt sai (đã xảy ra: G5 báo 100% trước khi có q15) | Mỗi lỗi thêm một câu; bộ DEP-002 giữ riêng |
| Giới hạn tốc độ của dịch vụ AI | Kiểm thử chậm/đỏ | Phản hồi giả cục bộ; breaker + retry đã có test |
| Mã đã vào `main` không qua PR | Không có bằng chứng review L2 cho phần lớn mã | Review lại theo lát ≤ 400 dòng (`review-record.md` §7); bật bảo vệ nhánh |
| Không có approver khác tác giả | Không thể hoàn tất L2 | Chỉ định người trước M2 (OQ-007) |
| Ảnh Docker bên thứ ba không kéo được (đã gặp với MinIO) | CI build đỏ vì hạ tầng | Ghim phiên bản; có phương án thay (SeaweedFS) |
| `RLIMIT_AS` không có hiệu lực trên macOS | Bảo vệ bộ nhớ khi trích PDF chưa được kiểm trên máy dev | Kiểm trên Linux/container trong CI |

## 16. Phê duyệt (IEEE 829 §5.16)

Agent không có quyền phê duyệt. Kế hoạch có hiệu lực khi đủ chữ ký:

| Vai trò | Họ tên | Quyết định | Ngày | Chữ ký |
|---|---|---|---|---|
| QA Lead | | ☐ Duyệt ☐ Duyệt có điều kiện ☐ Không duyệt | | |
| Product owner | | ☐ Duyệt ☐ Duyệt có điều kiện ☐ Không duyệt | | |
| CNTT / Bảo mật | | ☐ Duyệt ☐ Duyệt có điều kiện ☐ Không duyệt | | |

---

## Phụ lục A — Ma trận truy vết yêu cầu → ca kiểm thử

Nguồn: `make trace` (marker `@pytest.mark.req`, tên test web `[US-xxx-ACn]`). Kết quả lượt chạy 2026-10-28: xem `test-report.md` §4.

| AC | Ưu tiên | Đơn vị | Tích hợp | Web / E2E |
|---|---|---|---|---|
| US-001-AC1 | P0 | — | `test_upload_list_get` | smoke |
| US-001-AC2 | P0 | `test_upload_exact_limit_ok_one_byte_over_rejected` | `test_upload_rejections` | — |
| US-001-AC3 | P0 | `test_upload_rejects_non_pdf` (3 ca) | `test_upload_rejections` | `[US-001-AC3]`, smoke |
| US-002-AC1 | P0 | — | `test_ingestion_outcomes` (4 ca) | smoke |
| US-002-AC2 | P0 | — | `test_ask_answered_with_sources` | `[US-002-AC2]` |
| US-003-AC1 | P0 | `test_pdf_extractor_cases` | `test_ingestion_outcomes[corrupt]` | — |
| US-003-AC2 | P0 | `test_pdf_extractor_cases` | `test_ingestion_outcomes[encrypted]` | `[US-003-AC2]`, smoke |
| US-003-AC3 | P0 | `test_pdf_extractor_cases` | `test_ingestion_outcomes[image-only]` | — |
| US-003-AC4 | P0 | — | `test_upload_atomic_on_failures` | — |
| US-004-AC1 | P1 | — | `test_upload_list_get` | smoke |
| US-005-AC1 | P1 | — | `test_delete_is_immediate_everywhere` | `[US-005-AC1]`, smoke |
| US-005-AC2 | P1 | — | `test_delete_is_immediate_everywhere`, `test_race_deleted_between_retrieve_and_sources` | smoke |
| US-006-AC1 | P0 | — | `test_ask_answered_with_sources` | `[US-006-AC1]`, smoke |
| US-006-AC2 | P0 | — | — | `[US-006-AC2]` |
| US-006-AC3 | P0 | `test_prompt_rules_conflict_and_language` | — | — |
| US-007-AC1 | P0 | — | `test_ask_answered_with_sources` | `[US-007-AC1]` |
| US-007-AC2 | P0 | — | `test_multi_doc_sources` | smoke |
| US-008-AC1 | P1 | — | `test_source_pages_match` | `[US-008-AC1]` |
| US-009-AC1 | P0 | — | `test_multi_doc_sources` | smoke |
| US-009-AC2 | P0 | `test_prompt_rules_conflict_and_language` | — | — |
| US-010-AC1 | P0 | `test_grounding_validator` (7 ca), `test_extractive_cites_and_not_found` | `test_not_found_paths` | `[US-010-AC1]`, smoke, **eval q11–q15** |
| US-010-AC2 | P0 | — | `test_partial_requires_sources` | `[US-010-AC2]` |
| US-015-AC1 | P0 | — | — | Rà soát `deploy/DATA_LOCATION.md` (chờ OQ-005) |

**Trường hợp biên:** EC-01 → `[US-006-AC2]`; EC-02/03 → US-001-AC2/AC3; EC-04/05 → US-003; EC-06 → `test_upload_atomic_on_failures`; EC-07/EC-15 → `[EC-07]` (web), `test_ai_errors_mapped`; EC-08/09 → `test_question_validation`; EC-10 → US-010; EC-11 → US-009-AC2; EC-12 → không kiểm (OQ-014); EC-16 → `test_race_deleted_between_retrieve_and_sources` + chip "(đã xóa)".
