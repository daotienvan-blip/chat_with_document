# Biên bản review mã (Review Record) — "Chat với tài liệu" (MVP)

> **Chuẩn:** IEEE 1028-2008 (technical review). Checklist đã điền: `Code_Review_IEEE_1028_Checklist.xlsx` (cùng thư mục).
> **Mã biên bản:** CWD-RR-2026-10-28 · **Tầng:** **L1 — Agent review** (đã xong) → L2 người duyệt (chờ) → L3 inspection (chờ).
> **Agent KHÔNG approve, KHÔNG merge, KHÔNG deploy.** Mọi đánh giá ở đây là khuyến nghị cho người duyệt L2.

## 0. Tính độc lập — đọc trước

Agent thực hiện L1 (Claude) cũng là agent đã viết phần lớn mã được review. **L1 vì vậy không độc lập với tác giả** và có thể bỏ sót đúng những giả định mà tác giả đã đặt. Điều này không thay thế được L2: approver phải là người khác tác giả, đọc diff (không đọc bản tóm tắt này) và tự chấm rubric ở §8.

## 1. Mục tiêu và đối tượng review

| Mã | Đối tượng | Diff | Kích thước (dòng viết tay thêm) | Ghi chú |
|---|---|---|---|---|
| **RO-1** | PR "Giai đoạn 7: CI L0 + sửa lỗi kiểu" | Thay đổi chưa commit trên `ec18ff6` (`test-report.md` §7) | ~210 (+58/−10 tệp có sẵn, ~150 tệp mới) | ≤ 400 ✅ — sẵn sàng cho L2 |
| **RO-2** | Review hồi tố bản triển khai | `24c2c46..ec18ff6 -- app/` (bỏ `package-lock.json`, `generated.ts`) | **5.851** trong 112 tệp: `cwd_server` 2.383 · tests 1.181 · web 1.111 · deploy 460 · scripts 244 · eval 120 | **Vi phạm ≤ 400** — đã nằm trên `main` không qua PR (F-11) |

**Mục tiêu review (IEEE 1028 §6.1):** tìm lỗi (đúng/sai so với AC và thiết kế), kiểm tuân thủ kiến trúc SAD và quy ước mã, đánh giá an toàn và hiệu năng, xác nhận truy vết AC ↔ test.

## 2. Tiêu chí vào (đã kiểm)

| Đầu vào | Có? | Vị trí |
|---|---|---|
| Mã nguồn + diff | ✅ | git `24c2c46..ec18ff6`, thay đổi làm việc |
| Yêu cầu (BRD, PRD, user story có AC) | ✅ | `docs/02-requirements/`, `docs/03-analysis/` |
| Thiết kế (SAD, Blueprint, API, CSDL, OpenAPI) | ✅ | `docs/04-design/` |
| Kế hoạch triển khai + task | ✅ | `docs/05-implement/` |
| L0 xanh trên đúng mã được review | ✅ | `evidence/ci.log` — 10/10, 137 s |
| Kế hoạch kiểm thử | ✅ | `test-plan.md` |

## 3. Phương pháp

1. Chạy công cụ trước (L0): ruff, **mypy (lần đầu)**, import-linter, pytest + coverage, vitest + coverage, gitleaks, build ảnh. Mọi phát hiện của công cụ được sửa hoặc ghi nhận trước khi đọc mã.
2. Đọc toàn bộ các tệp có rủi ro cao theo `test-plan.md` §2.6: `api/app.py`, `persistence/repositories.py`, `core/documents/{service,validate_upload}.py`, `core/ingestion/service.py`, `core/retrieval/service.py`, `core/answer/{service,prompt}.py`, `core/guard`, `worker/{runner,maintenance}.py`, `adapters/{llm_local,llm_http,resilient_llm,stores,s3_store,pymupdf_extractor}.py`, `platform/logging.py`, `web/src/api-client/client.ts`, `deploy/proxy/*.conf`. Quét có mục tiêu phần còn lại của web (điểm chèn HTML, `target=_blank`, bộ hẹn giờ).
3. Tái hiện mọi nghi vấn trước khi ghi nhận: DEF-001 được tái hiện bằng `make eval` (q15) và phân tích trọng số từng câu.
4. Mỗi phát hiện có trích dẫn tệp:dòng (theo mã sau giai đoạn 7), tiêu chí rubric bị ảnh hưởng và đề xuất cụ thể.

**Không đọc toàn bộ:** test (chỉ đọc theo nhu cầu đối chiếu), `scripts/`, `eval_cwd/run.py`, CSS, `components/` web. L2 cần phủ các phần này (§7).

## 4. Phát hiện

Mức: **Major** = vi phạm AC/cổng Must hoặc rủi ro an toàn/vận hành có thể xảy ra; **Minor** = sai lệch không phá AC P0; **Góp ý** = cải thiện.

| Mã | Mức | Tệp:dòng | Phát hiện | Rubric | Đề xuất | Trạng thái |
|---|---|---|---|---|---|---|
| **F-01** | **Major** | `adapters/llm_local.py:116-117`, `:128-135`; `platform/config.py:53` | **DEF-001.** Câu ngoài tài liệu được trả `answered`. (1) So khớp cả dạng bỏ dấu ⇒ "tỷ"≡"ty", "đã"≡"đà"; (2) độ phủ cộng dồn qua các câu không liên quan ở nhiều tài liệu (0.38 + 0.25 ≥ 0.6); (3) `rag_min_relevance=0.0` tắt G-L1. Vi phạm US-010-AC1, G5 = 80% | Đúng AC | Xem `test-report.md` §5; PR riêng kèm ca hồi quy q15 | Mở |
| **F-02** | **Major** | `persistence/repositories.py:180-182`; `worker/runner.py:16-23` | `release_overdue` đưa việc quá hạn khóa về `queued` mà **không xét `attempts`**; `claim` cũng không lọc. `MAX_ATTEMPTS` chỉ được áp khi handler ném ngoại lệ. Nếu worker chết giữa việc (OOM-kill, SIGKILL, mất node), việc đó được nhận lại vô hạn, cứ mỗi `lock_minutes` một lần: một PDF gây chết worker sẽ làm worker chết lặp lại, và tài liệu kẹt ở `processing` mãi mãi (US-002) | Hiệu năng, Đúng AC | Trong `release_overdue`: `attempts >= MAX_ATTEMPTS` ⇒ `failed` + `set_failed(PROCESSING_ERROR)`; thêm test tích hợp mô phỏng khóa hết hạn 3 lần | Mở |
| **F-03** | **Major** | `platform/config.py:41`; `api/app.py:188`; `deploy/proxy/nginx.conf:14`, `:47` | Khi `MAX_QUESTION_LENGTH` để trống (mặc định, chờ OQ-P06) thì **không có giới hạn cứng** độ dài câu hỏi; `client_max_body_size 210m` áp cho cả `/api/v1/questions`. Một câu hỏi ~200 MB được parse, tạo embedding và (với `LLM_PROVIDER=http`) gửi ra dịch vụ AI ⇒ tốn bộ nhớ và chi phí, mở đường DoS. Tải lên đã có giới hạn cứng tương tự (`hard_max_upload_mb`) nhưng câu hỏi thì không | An toàn, Hiệu năng | Thêm `hard_max_question_chars` (đề xuất 4.000) giống `effective_limit_mb`; `client_max_body_size 64k` riêng cho location câu hỏi; test biên | Mở |
| F-04 | Minor | `api/app.py:69-70` → `:79-85` | Phản hồi 429 của bộ giới hạn trong ứng dụng `return` từ trong `try`, bỏ qua đoạn gắn `X-Request-Id` + `nosniff` và đếm metrics. Thân problem+json vẫn có `requestId` | Đúng AC (API_Design: mọi phản hồi có `X-Request-Id`) | Gán `resp = problem(...)` thay vì `return` | Mở |
| F-05 | Minor | `api/app.py:100-101` | `/readyz` nuốt ngoại lệ, không ghi log ⇒ vận hành chỉ thấy 503 mà không biết phụ thuộc nào hỏng | Dễ đọc/Vận hành | `log.warning(..., extra={"event": "not_ready", "errorCode": type(e).__name__})` | Mở |
| F-06 | Minor | `adapters/llm_http.py:37`, `:41` | `r.json()` và `data["data"]` không được bọc: dịch vụ AI trả 200 với thân không phải JSON hoặc sai cấu trúc ⇒ `JSONDecodeError`/`KeyError` ⇒ API trả 500 `INTERNAL_ERROR` (thay vì `AI_UNAVAILABLE`), còn ingestion thất bại hẳn thay vì thử lại | An toàn (xử lý lỗi) | Bọc thành `AiBadOutput`/`AiUnavailable`; thêm ca vào `test_http_llm_errors` | Mở |
| F-07 | Minor | `core/guard/__init__.py:35`, `:46`, `:49` | `RateLimiter._buckets` không bao giờ được dọn ⇒ bộ nhớ tăng theo số địa chỉ khách khác nhau. Chỉ ảnh hưởng khi chạy trực tiếp (demo), vì sản xuất tắt bộ giới hạn trong ứng dụng | Hiệu năng | Dọn các bucket đã đầy (tokens = cap) định kỳ, hoặc dùng LRU có giới hạn | Mở |
| F-08 | Minor | `web/src/features/documents/documents.tsx:110`, `:119`, `:236` | `justReady` chỉ được thêm, không bao giờ xóa ⇒ băng "Tài liệu đã sẵn sàng để hỏi" ở lại trên mọi thẻ đã chuyển sang sẵn sàng trong phiên (quan sát trên trình duyệt thật) | Đúng AC (US-002-AC1 vẫn đạt), UX | Tự ẩn sau vài giây hoặc khi người dùng gửi câu hỏi | Mở |
| F-09 | Góp ý | `core/ingestion/service.py:43`; `adapters/pymupdf_extractor.py:54-57` | Đọc toàn bộ tệp vào bộ nhớ rồi chép sang tiến trình con ⇒ đỉnh bộ nhớ ~2–3× kích thước tệp mỗi worker (tới ~600 MB với giới hạn 200 MB). Chấp nhận được cho MVP | Hiệu năng | Ghi vào hướng dẫn định cỡ worker; cân nhắc truyền đường dẫn tệp tạm | Ghi nhận |
| F-10 | Góp ý | `platform/logging.py:17-33`; `tests/integration/test_flows.py:437-446` | Test "không lộ nội dung" bắt log qua `caplog` nên **không đi qua `JsonFormatter`** (coverage 28%). Formatter là nơi quyết định trường nào được in | Test | Thêm test định dạng: bản ghi có trường lạ/`exc_info` ⇒ chỉ in trường cho phép + tên lớp ngoại lệ | Mở |
| **F-11** | **Major (quy trình)** | `main` @ `ec18ff6` | 5.851 dòng viết tay vào `main` trực tiếp, không PR, không approver ≠ tác giả, chưa có CI tại thời điểm đó. Vi phạm quy tắc PR ≤ 400 dòng và L2 | Truy vết | Bật bảo vệ nhánh; review hồi tố theo lát (§7); từ nay mọi thay đổi qua PR | Mở — cần chủ repo |
| F-12 | Góp ý | `web/src/api-client/client.ts:51` | Listener `abort` trên `signal` ngoài không được gỡ sau khi yêu cầu xong (rò rỉ nhỏ mỗi câu hỏi) | Hiệu năng | `{ once: true }` + gỡ trong `finally` | Mở |
| F-13 | Minor | `api/app.py:69` (trước sửa) + 7 vị trí kiểu | **DEF-002**: `except Exception as e: … e.code` ⇒ AttributeError nếu bộ giới hạn ném lỗi khác `RateLimited`; 7 lỗi kiểu còn lại không đổi hành vi | An toàn | Đã thu hẹp thành `except RateLimited`; thêm mypy vào L0 | **Đã sửa** (RO-1) |
| F-14 | Minor | `.github/workflows/ci.yml` (job `secrets`) | Tự soát RO-1: bản đầu tải gitleaks qua `curl \| tar` không kiểm checksum (chuỗi cung ứng) | An toàn | Kiểm SHA-256 theo `checksums.txt` chính thức | **Đã sửa** (RO-1) |

**Điểm mạnh đã xác minh** (để người duyệt L2 không phải đi tìm lại):
- Mọi truy vấn SQL dùng tham số; f-string duy nhất ghép giá trị là `int(ef_search)` (`repositories.py:112`). Bộ lọc "searchable" nằm ở một hằng số (`repositories.py:20`) và được dùng cho mọi truy vấn đọc `chunks`.
- G-L3: nguồn được tra lại từ CSDL sau khi LLM trả lời (`answer/service.py:47-50`), nên tài liệu bị xóa giữa chừng không lọt vào câu trả lời (có test đua).
- Tải lên nguyên tử có bù trừ (`documents/service.py:24-41`); purge xóa tệp trước rồi mới xóa bản ghi (`maintenance.py:19-33`).
- PDF không tin cậy được xử lý trong tiến trình con có hạn thời gian và `RLIMIT_AS` (`pymupdf_extractor.py`); lưu ý `RLIMIT_AS` không hiệu lực trên macOS.
- Log chỉ in trường trong danh sách cho phép (`logging.py:12`); có test canary.
- Kiến trúc ports & adapters được import-linter ép bằng 3 hợp đồng; phân quyền CSDL được kiểm bằng vai trò đăng nhập thật.
- Biểu tượng SVG dùng `dangerouslySetInnerHTML` (`Icon.tsx:6`) nhưng chỉ lấy từ hằng `ICONS`, không có dữ liệu người dùng ⇒ an toàn. Liên kết nguồn có `rel="noopener"`.

## 5. Rubric 7 tiêu chí (0 = không đạt · 1 = đạt một phần · 2 = đạt)

Ngưỡng merge: **≥ 10/14**, và không còn phát hiện Major mở trong chính diff đó.

| Tiêu chí | RO-1 (PR giai đoạn 7) | Lý do | RO-2 (hồi tố `ec18ff6`) | Lý do |
|---|---|---|---|---|
| Đúng AC | 1 | Đủ mọi mục L0 và xanh cục bộ; **chưa chạy trên GitHub runner** — đó mới là L0 thật | 1 | 22/23 AC có test đạt, nhưng US-010-AC1 không đạt trên demo (F-01) |
| Test | 2 | Workflow đã chạy đầy đủ qua `make ci`; thêm ca hồi quy q15 | 2 | 85 test, coverage 83%/80.6%, tích hợp trên PostgreSQL thật, kiểm hợp đồng OpenAPI; thiếu E2E trình duyệt (S8-08), F-10 |
| Thiết kế | 2 | CI và `make ci` cùng một danh sách bước; job song song; ngưỡng nằm trong cấu hình công cụ, không rải trong script | 2 | Khớp SAD (module, ports & adapters, hàng đợi trong PostgreSQL); các khác biệt có ghi trong `IMPLEMENTATION_STATUS.md` |
| An toàn | 2 | `permissions: contents: read`; gitleaks kiểm checksum, `--redact`; thu hẹp `except` | 1 | Nhiều lớp phòng vệ tốt (§4), nhưng F-03 (không giới hạn câu hỏi), chưa quét lỗ hổng phụ thuộc (SEC-10) |
| Hiệu năng | 2 | 137 s ≪ 600 s; cache pip/npm | 1 | Spike truy xuất tốt (p95 27 ms), nhưng F-02 (lặp vô hạn), F-07, F-09 |
| Dễ đọc | 2 | Script ngắn, bước có tên; chú thích nêu lý do | 2 | Đặt tên nhất quán; docstring trỏ về mục thiết kế; ruff + mypy sạch |
| Truy vết | 2 | Mọi bước trỏ về `test-plan.md`; bằng chứng lưu trong `evidence/` | 1 | Marker `req` + `make trace` rất tốt, **nhưng không có PR/approval** cho 5.851 dòng (F-11) |
| **Tổng** | **13/14** | | **10/14** | |

**Khuyến nghị của agent (không phải phê duyệt):**
- **RO-1:** đủ điều kiện đưa sang L2. Approver kiểm thêm: lượt CI đầu tiên trên GitHub xanh và dưới 10 phút; cấu hình `fail_under`/`thresholds` không bị hạ.
- **RO-2:** đạt đúng ngưỡng 10/14 nhưng còn **3 Major** (F-01, F-02, F-03) và F-11 ⇒ **"Chấp nhận có điều kiện"**: không phát hành trước khi F-01…F-03 được sửa qua PR có review, và L2 hoàn tất review hồi tố theo lát.

## 6. Kết quả checklist IEEE 1028 (tóm tắt — chi tiết trong tệp xlsx)

| Nhóm | Mục | Kết quả L1 |
|---|---|---|
| 1. Chuẩn bị | Mục tiêu review / Tiêu chí vào | Đạt / Đạt |
| 2. Kiến trúc | Tuân thủ thiết kế / Tính module | Đạt / Đạt |
| 3. Logic | Phủ yêu cầu (không thêm tính năng ngoài phạm vi) | Đạt một phần — F-01 |
| | Điều kiện biên | Đạt một phần — F-03 (biên trên của câu hỏi); biên tải lên đã có test ±1 byte |
| | Khởi tạo biến | Đạt — mypy sạch |
| 4. Xử lý lỗi | Bắt ngoại lệ đúng tầng | Đạt một phần — F-06, F-13 (đã sửa) |
| | Thông điệp lỗi | Đạt — problem+json, tiếng Việt, không lộ chi tiết nội bộ; F-05 |
| 5. Bảo mật | Kiểm tra đầu vào | Đạt một phần — F-03 |
| | Xác thực/phân quyền | Đạt theo thiết kế (không đăng nhập, CON-005): allowlist mạng + phân quyền CSDL; rủi ro RSK-P03 đã được chấp nhận ở PRD |
| 6. Hiệu năng | Quản lý tài nguyên | Đạt một phần — F-02, F-07, F-12 |
| | Hiệu quả thuật toán | Đạt — quét chính xác có số đo; RRF O(n log n) |
| 7. Dễ bảo trì | Chuẩn mã / Đặt tên / Chú thích | Đạt / Đạt / Đạt |
| 8. Kiểm thử | Coverage / Test đạt | Đạt (83%, 80.6%) / Đạt (85/85) |
| 9. Tiêu chí ra | Phát hiện đã ghi, sửa, xác minh | **Chưa** — 2/14 đã sửa và xác minh; 11 mở; 1 ghi nhận |

## 7. Kế hoạch cho L2, L3, L4

**L2 — review hồi tố RO-2 theo lát ≤ 400 dòng** (approver ≠ tác giả, đọc diff bằng `git diff 24c2c46 ec18ff6 -- <đường dẫn>`):

| Lát | Đường dẫn | ~Dòng |
|---|---|---|
| L2-1 | `server/cwd_server/api/`, `core/errors.py`, `core/guard/` | ~400 |
| L2-2 | `server/cwd_server/core/documents/`, `core/ingestion/`, `adapters/pymupdf_extractor.py` | ~350 |
| L2-3 | `server/cwd_server/core/retrieval/`, `core/answer/`, `adapters/llm_*.py`, `adapters/resilient_llm.py` | ~400 |
| L2-4 | `server/cwd_server/persistence/`, `worker/`, `adapters/stores.py`, `adapters/s3_store.py` | ~450 (tách đôi nếu cần) |
| L2-5 | `server/cwd_server/platform/`, `container.py`, `ports/` | ~300 |
| L2-6…8 | `web/src/` (api-client + state; documents; chat + sources + components) | ~1.100 |
| L2-9…11 | `server/tests/` | ~1.180 |
| L2-12 | `deploy/` (compose, Dockerfile, proxy, script) | ~460 |

**L3 — inspection IEEE 1028 (nhóm, có người điều phối, đọc theo checklist) cho các diff rủi ro cao.** Dự án không có xác thực, thanh toán hay PII có cấu trúc, nhưng có các vùng tương đương:

| Vùng | Lý do rủi ro cao | Người tham gia |
|---|---|---|
| Tải tệp + trích PDF (`validate_upload.py`, `pymupdf_extractor.py`) | Đầu vào không tin cậy, trình phân tích C | Dev + bảo mật |
| Xóa/purge/đối soát + versioning S3 (`maintenance.py`, `documents/service.py`, lifecycle) | Xóa không hoàn tác; dữ liệu phải thật sự biến mất (BR-004, RSK-002) | Dev + vận hành |
| Dữ liệu gửi ra dịch vụ AI (`llm_http.py`, `prompt.py`) | Nội dung tài liệu rời hệ thống (OQ-005) | Dev + CNTT/pháp lý |
| Phân quyền CSDL + proxy (`schema.sql` GRANT, `init-roles.sh`, `nginx.conf`) | Lớp kiểm soát truy cập duy nhất khi không có đăng nhập | Dev + bảo mật |

**L4 — xác nhận với stakeholder:** demo 13 use case với business owner theo `guide/HUONG_DAN_SU_DUNG.md`, trình bày DEF-001 và giới hạn của AI giả; UAT theo `test-plan.md` §6.6 khi OQ-004/OQ-005 đóng.

## 8. Phê duyệt L2 — người duyệt điền

> Đọc diff, không đọc tóm tắt. Chấm độc lập (không chép điểm của agent ở §5). Approver phải khác tác giả.
> Hướng dẫn chấm và điều kiện người duyệt: `l2-reviewer-guide.md`.

**Chỉ định người duyệt (2026-10-28):** **chưa có** — `[TBD]`, chờ chủ dự án chỉ định. Không đủ điều kiện: Dao Tien Van (tác giả mọi commit trên `main`), agent (người viết mã). Khi chưa có người duyệt, L2 = chưa đạt và không được merge/phát hành.

| PR / lát | Người duyệt | Đúng AC | Test | Thiết kế | An toàn | Hiệu năng | Dễ đọc | Truy vết | Tổng /14 | Quyết định | Ngày |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RO-1 | | | | | | | | | | ☐ Approve ☐ Request changes | |
| L2-1 | | | | | | | | | | ☐ Approve ☐ Request changes | |
| L2-2 | | | | | | | | | | ☐ Approve ☐ Request changes | |
| … | | | | | | | | | | | |

| Inspection L3 | Người điều phối | Người đọc | Số lỗi tìm thêm | Kết luận | Ngày |
|---|---|---|---|---|---|
| | | | | ☐ Chấp nhận ☐ Chấp nhận có điều kiện ☐ Làm lại | |
