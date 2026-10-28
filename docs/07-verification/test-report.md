# Báo cáo tổng kết kiểm thử (Test Summary Report) — "Chat với tài liệu" (MVP)

> **Chuẩn:** IEEE 829-2008 §11 (Level Test Report / Master Test Report). **Kế hoạch:** `test-plan.md` (CWD-MTP-v1.0).
> **Mã báo cáo:** CWD-TSR-2026-10-28 · **Lượt:** M1 — Xác minh (giai đoạn 7) · **Người lập:** Agent (Claude) — không có quyền phê duyệt.

## 1. Tóm tắt

| Mục | Kết quả |
|---|---|
| Phiên bản được kiểm | `main` @ `ec18ff6` + thay đổi giai đoạn 7 chưa commit (CI, mypy, sửa kiểu, ca eval q15) — danh sách §7 |
| L0 — CI cục bộ (`make ci`) | ✅ **XANH** — 10/10 bước, **137 s** (giới hạn 600 s) |
| Test tự động | ✅ **85/85 đạt** (server: 48 đơn vị + 29 tích hợp; web: 8) — 0 lỗi, 0 bỏ qua |
| Coverage | ✅ Server **83%** (câu lệnh + nhánh) · Web **80.6%** dòng / 72.7% nhánh — cổng ≥ 70% |
| Quét bí mật (gitleaks, toàn bộ lịch sử git) | ✅ 0 phát hiện (1 báo nhầm đã xem xét và ghi nhận) |
| Khói đầu-cuối (`make smoke`) | ✅ 17/17 |
| Proxy (`make proxy-test`) | ✅ 13/13 |
| Truy vết AC | 22/23 AC có test tự động đạt; US-015-AC1 chờ OQ-005 |
| Đánh giá AI (`make eval`, 15 câu) | ❌ **G5 = 80%** (yêu cầu 100%) — DEF-001 · G4 = 100% · ổn định 100% |
| Lỗi mở | **1 Major** (DEF-001) + 2 Major từ review mã (F-02, F-03) + 6 Minor — `review-record.md` |
| **Kết luận** | **Chưa đủ điều kiện phát hành.** L0 đạt; cổng G5 không đạt trên bản demo; G3, G8, G12 bị chặn bởi OQ; L2 (người duyệt) chưa thực hiện |

## 2. Sai khác so với kế hoạch

| Sai khác | Lý do | Ảnh hưởng |
|---|---|---|
| CI chạy cục bộ (`make ci`), chưa chạy trên GitHub Actions | Workflow vừa được thêm, chưa commit/push (agent không tự push) | Bằng chứng L0 là log cục bộ; lượt CI đầu tiên trên GitHub phải được kiểm khi mở PR |
| Mã đã nằm trên `main` không qua PR | Có từ trước giai đoạn 7 | L2 phải review lại theo lát — `review-record.md` §7 |
| Chưa chạy E2E trình duyệt + axe (S8-08), quét lỗ hổng phụ thuộc (SEC-10) | Ngoài phạm vi lượt M1 | ACC-01…04 và G9 chưa có bằng chứng tự động |
| Hệ thống chạy cho `make smoke` là bản demo đang chạy (mã trước khi sửa kiểu ở giai đoạn 7) | Các sửa đổi chỉ là chú thích kiểu + thu hẹp `except`; được phủ bởi 85 test | Thấp |

## 3. Kết quả theo bộ kiểm thử

| Bộ | Số ca | Đạt | Lỗi | Thời gian | Bằng chứng |
|---|---|---|---|---|---|
| ruff (lint) | — | ✅ | 0 | < 1 s | `evidence/ci.log` |
| mypy (kiểu Python, **mới**) | 46 tệp | ✅ | 0 (trước khi sửa: 8) | 1 s | `evidence/ci.log` |
| import-linter | 3 hợp đồng | ✅ | 0 | < 1 s | `evidence/ci.log` |
| REG-01 Đơn vị server | 48 | 48 | 0 | | `evidence/ci.log` |
| REG-02 Tích hợp + hợp đồng API | 29 | 29 | 0 | 30 s (cả hai) | `evidence/ci.log` |
| REG-01 Web (tsc + vitest) | 8 | 8 | 0 | 4 s | `evidence/ci.log` |
| Build web (vite) | — | ✅ | 0 | 1 s | `evidence/ci.log` |
| gitleaks | 4 commit | ✅ | 0 | < 1 s | `evidence/ci.log` |
| Build ảnh `cwd-server`, `cwd-web` | 2 | ✅ | 0 | 101 s | `evidence/ci.log` |
| REG-03 Khói | 17 | 17 | 0 | | `evidence/smoke.log` |
| REG-04 Proxy | 13 | 13 | 0 | | `evidence/proxy-test.log` |
| REG-05 Đánh giá AI | 15 | 14 | **1** (q15) | | `evidence/eval-report.md` |

## 4. Kết quả theo tiêu chí chấp nhận

| AC | Ưu tiên | Kết quả | Ghi chú |
|---|---|---|---|
| US-001-AC1, AC2, AC3 | P0 | ✅ Đạt | Giá trị giới hạn thật chờ OQ-009 (đang dùng `HARD_MAX_UPLOAD_MB=200`) |
| US-002-AC1, AC2 | P0 | ✅ Đạt | |
| US-003-AC1…AC4 | P0 | ✅ Đạt | |
| US-004-AC1 | P1 | ✅ Đạt | |
| US-005-AC1, AC2 | P1 | ✅ Đạt | Gồm ca đua: xóa giữa lúc truy xuất và lúc dựng nguồn |
| US-006-AC1 | P0 | ✅ Đạt (cơ chế) | Độ đúng nội dung thuộc G3 — chưa đánh giá |
| US-006-AC2, AC3 | P0 | ✅ Đạt | |
| US-007-AC1, AC2 | P0 | ✅ Đạt | G4 = 100% trên bộ tổng hợp |
| US-008-AC1 | P1 | ✅ Đạt | |
| US-009-AC1, AC2 | P0 | ✅ Đạt | AC2 kiểm ở mức lời nhắc (quy tắc 4), chưa kiểm với mô hình thật |
| **US-010-AC1** | **P0** | **❌ Không đạt trên bản demo** | Test tự động đạt (cơ chế G-L2 đúng), nhưng `ExtractiveLlm` trả lời câu ngoài tài liệu — **DEF-001** |
| US-010-AC2 | P0 | ✅ Đạt | |
| US-015-AC1 | P0 | ⛔ Bị chặn | OQ-005 |

**Ghi chú về US-010-AC1:** các test tự động kiểm *cơ chế* (G-L2 hạ cấp khi trích dẫn không hợp lệ; G-L1 khi không có đoạn nào). Chúng dùng `FakeLlm` có kịch bản nên không phát hiện được việc mô hình trả `answered` kèm mã trích dẫn hợp lệ cho câu ngoài phạm vi. Khoảng trống này chỉ lộ ra ở mức đánh giá AI (REG-05) và trên trình duyệt thật.

## 5. Lỗi phát hiện

| Mã | Mức | Tóm tắt | AC / cổng | Trạng thái |
|---|---|---|---|---|
| **DEF-001** | **Major** | Câu ngoài tài liệu "Công ty có bao nhiêu nhân viên ở chi nhánh Đà Nẵng?" nhận `answered`, trích 2 tài liệu không liên quan | US-010-AC1, G5 | **Mở** — chi tiết dưới |
| DEF-002 | Minor | 8 lỗi kiểu (mypy) chưa từng được kiểm, gồm 1 lỗi thật: `except Exception` ở middleware giới hạn tốc độ đọc `e.code` → AttributeError nếu bộ giới hạn ném lỗi khác | — | **Đã sửa** ở giai đoạn 7 (`api/app.py:69`) |
| DEF-003 | Góp ý | gitleaks báo `cwd.conversation.v1` (tên khóa sessionStorage) là khóa API | — | Đóng — báo nhầm, ghi trong `.gitleaksignore` |

Các phát hiện từ review mã (F-02 hàng đợi lặp vô hạn khi worker chết, F-03 câu hỏi không giới hạn độ dài, …) nằm trong `review-record.md` §4.

### DEF-001 — chi tiết

- **Tái hiện:** `make samples && make eval` → câu `q15` trong `app/server/eval_cwd/datasets/synthetic.jsonl`. Phát hiện lần đầu trên trình duyệt thật khi chụp ảnh cho `guide/` (2026-10-28).
- **Thực tế:** `answered`, nguồn `hop-dong-A.pdf`, `quy-dinh-C.pdf`. **Mong đợi:** `not_found`.
- **Nguyên nhân gốc (3 lớp):**
  1. `adapters/llm_local.py:116-117` so khớp cả dạng bỏ dấu ⇒ "tỷ" ≡ "ty", "đã" ≡ "đà". Trong tiếng Việt, dấu mang nghĩa, nên bỏ dấu tạo trùng khớp sai.
  2. `adapters/llm_local.py:128-135` cộng độ phủ từ khóa qua **nhiều câu không liên quan, thuộc các tài liệu khác nhau**: câu "Nhân viên đi công tác…" (0.38) + câu "Tổng giá trị hợp đồng là 1,2 tỷ đồng, đã bao gồm…" (0.25) = 0.63 ≥ ngưỡng 0.6.
  3. `platform/config.py:53` `rag_min_relevance = 0.0` ⇒ cổng G-L1 chỉ chặn khi không có đoạn nào; vì truy xuất vector luôn trả đoạn, mọi câu hỏi đều tới LLM.
- **Phạm vi ảnh hưởng:** chỉ bản demo dùng `ExtractiveLlm`. Với mô hình thật, lớp 3 vẫn còn: hành vi G5 phụ thuộc hoàn toàn vào mô hình, chưa đánh giá được (OQ-004/005).
- **Đề xuất sửa (PR riêng, ≤ 400 dòng):** (a) chỉ so khớp có dấu khi câu hỏi có dấu; (b) tính độ phủ trên từng câu hoặc từng tài liệu, không cộng chéo tài liệu; (c) hiệu chỉnh `RAG_MIN_RELEVANCE` bằng bộ DEP-002; (d) giữ `q15` làm ca hồi quy và thêm vài câu "trùng từ phổ biến" khác.
- **Tài liệu bị ảnh hưởng:** `docs/05-implement/release-gates.md` ghi G5 "Đạt (demo)" — **không còn đúng**, đã cập nhật (§8).

## 6. Đánh giá chất lượng AI

| Chỉ số | Kết quả | Ngưỡng | Đạt? |
|---|---|---|---|
| G5 — ngoài tài liệu → `not_found` | 4/5 = **80%** | 100% | ❌ |
| G4 — nguồn đúng tài liệu | 100% | 100% | ✅ |
| Nguồn phủ đủ tài liệu kỳ vọng | 100% | — | ✅ |
| Trang đúng | 100% | — | ✅ |
| Ổn định | 100% | 100% | ✅ |
| G3 — độ đúng nội dung | Chưa chấm | `[TBD: OQ-004]` | ⛔ |

Quan sát: `q03` ("Thiết bị được bảo hành bao lâu?") trả `partial` thay vì `answered`. Bộ đánh giá hiện tính `partial` là "có trả lời" nên không báo lỗi; nên tách thành chỉ số riêng.

## 7. Thay đổi trong lượt này (để review L2)

| Tệp | Thay đổi | Loại |
|---|---|---|
| `.github/workflows/ci.yml` | Workflow L0: server (ruff, mypy, import-linter, pytest + coverage trên pgvector), web (tsc, vitest + coverage, build), gitleaks, build ảnh; mỗi job ≤ 10 phút | Mới |
| `app/deploy/ci-local.sh`, `app/Makefile` (`make ci`) | L0 cục bộ, ghi log + coverage vào `app/var/ci/` | Mới |
| `.gitleaksignore` | 1 báo nhầm đã xem xét | Mới |
| `app/server/pyproject.toml` | Thêm `pytest-cov`, `mypy`; cấu hình mypy; `fail_under = 70` | Cấu hình |
| `app/web/vite.config.ts`, `package.json`, `package-lock.json` | `@vitest/coverage-v8`; ngưỡng 70% | Cấu hình |
| `app/server/cwd_server/api/app.py` | `except Exception` → `except RateLimited` (DEF-002) | Sửa lỗi |
| `core/retrieval/service.py`, `core/documents/validate_upload.py`, `worker/runner.py`, `adapters/pymupdf_extractor.py` | Chú thích kiểu cho mypy; không đổi hành vi | Kiểu |
| `app/server/eval_cwd/datasets/synthetic.jsonl` | Ca hồi quy `q15` (DEF-001) | Test |
| `app/.gitignore` | Bỏ qua `.coverage`, `coverage.xml`, `junit.xml`, `.mypy_cache/` | Cấu hình |

## 8. Trạng thái cổng phát hành sau lượt này

| Cổng | Trước (2026-10-27) | Sau (2026-10-28) |
|---|---|---|
| G1 | Chưa (US-015, chưa UAT) | Chưa — thêm US-010-AC1 không đạt trên demo |
| G2 | Chưa (không có hệ thống theo dõi lỗi) | **Chưa — 1 lỗi Major mở với P0 (DEF-001)**; tạm theo dõi trong báo cáo này |
| G4 | Đạt (demo) | Đạt (demo) |
| G5 | Đạt (demo) | **Không đạt — 80%** |
| G9 | Chưa | Chưa — đã có quét bí mật (0), còn thiếu quét lỗ hổng phụ thuộc/ảnh |
| G3, G8, G12 | Chặn | Chặn (OQ-004, OQ-005) |

## 9. Khuyến nghị

1. **Không phát hành.** Không merge thêm tính năng trước khi sửa DEF-001 (Major, P0).
2. Commit thay đổi §7 trên nhánh riêng, mở PR để CI chạy lần đầu trên GitHub, rồi người duyệt ≠ tác giả review theo `review-record.md`.
3. Bật bảo vệ nhánh `main`: bắt buộc workflow `ci` xanh + 1 approval; cấm push trực tiếp.
4. Sửa DEF-001, F-02, F-03 trong các PR riêng, mỗi PR kèm ca hồi quy.
5. Làm S8-08 (Playwright + axe) và quét lỗ hổng (SEC-10) trước M4.

## 10. Phê duyệt báo cáo

| Vai trò | Họ tên | Quyết định | Ngày |
|---|---|---|---|
| QA Lead | | ☐ Chấp nhận báo cáo ☐ Yêu cầu bổ sung | |
| Product owner | | ☐ Chấp nhận báo cáo ☐ Yêu cầu bổ sung | |
