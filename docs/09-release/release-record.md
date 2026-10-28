# Release record — "Chat với tài liệu" v0.1.0 (MVP)

> **Mã:** CWD-REL-0.1.0 · **Ngày lập:** 2026-10-28 · **Người lập:** agent (Claude) — chỉ chuẩn bị hồ sơ.
> **Agent KHÔNG authorize, KHÔNG deploy, KHÔNG thay đổi production.** Mọi ô "Quyết định" dưới đây do người điền.

## 0. Kết luận hiện tại

**NO-GO — chưa phát hành.** Chưa có môi trường đích (OQ-005), commit ứng viên chưa qua L2, CI trên `main` đang đỏ, và còn 3 lỗi Major. Hồ sơ này là kế hoạch phát hành đã sẵn sàng để dùng khi các điều kiện ở §3 được gỡ.

## 1. Ứng viên phát hành

| Mục | Giá trị | Kiểm chứng |
|---|---|---|
| Phiên bản | `0.1.0` (`app/server/pyproject.toml`, `app/web/package.json`) | ✅ khớp nhau |
| Commit ứng viên | `b80b758` (merge PR #1 vào `main`) | — |
| Commit đã review (L1) | `3414187` (nội dung PR #1) | `docs/07-verification/review-record.md` RO-1 |
| Duyệt L2 trên PR #1 | **0 review**; PR do tác giả tự merge (`daotienvan-blip`) lúc 2026-10-28 14:00 UTC | GitHub API `pulls/1/reviews` = `[]` ⇒ **không đạt** |
| CI trên commit ứng viên | **Đỏ** — job `server`, bước test: `test_pdf_extractor_cases` (runner Ubuntu thiếu font tiếng Việt) | Run 40701720647; tái hiện trong container Linux. Sửa ở nhánh `fix/ci-vietnamese-font` (INC-2026-10-28-01) |
| Tag git | Chưa có | Tạo `v0.1.0` **chỉ** trên commit đã duyệt và CI xanh |

### 1.1 Artifact = commit đã review?

**Chưa chứng minh được.** Ảnh Docker hiện có (`cwd-server:local`, `cwd-proxy:local`) gắn tag `local` và **không có nhãn commit**:

| Ảnh | ID | Nhãn `org.opencontainers.image.revision` |
|---|---|---|
| `cwd-server:local` | `9b049eb59026` (27 giờ trước — dựng trước giai đoạn 7) | trống |
| `cwd-proxy:local` | `6a552137a548` | `d5fb0119…` — **của ảnh nền nginx**, không phải repo này (dễ gây nhầm) |

**Quy trình bắt buộc trước khi deploy** (REL-B1, chưa làm):
1. Dựng ảnh trong CI từ đúng commit có tag, truyền `--build-arg GIT_SHA=$GITHUB_SHA` và đặt `LABEL org.opencontainers.image.revision=$GIT_SHA` trong `Dockerfile.server`, `Dockerfile.web` (ghi đè nhãn kế thừa).
2. Gắn tag ảnh bằng SHA (`cwd-server:<sha>`), đẩy lên registry của tổ chức; triển khai **theo digest**, không theo tag.
3. Người authorize so: `git rev-parse v0.1.0^{commit}` = nhãn revision của ảnh = commit có approval L2.

## 2. Phạm vi và release notes

Xem `release-notes.md`.

## 3. Điều kiện Go (tất cả phải ✅)

| # | Điều kiện | Nguồn | Trạng thái 2026-10-28 |
|---|---|---|---|
| R1 | CI xanh trên commit ứng viên (4 job) | `.github/workflows/ci.yml` | ❌ đỏ — chờ PR sửa font |
| R2 | L2 approve (≠ tác giả) cho mọi thay đổi trong bản phát hành | `review-record.md` §8 | ❌ chưa chỉ định người duyệt; PR #1 không có review |
| R3 | Bảo vệ nhánh `main` (CI + 1 approval) | `review-record.md` F-11 | ❌ chưa bật (PR #1 merge được khi CI đỏ) |
| R4 | Không còn Major mở: DEF-001/F-01, F-02, F-03 | `review-record.md` §4 | ❌ 3 mở |
| R5 | Cổng PRD G1–G13 | `docs/05-implement/release-gates.md` | ❌ G2, G3, G5, G8, G9, G12, G13 chưa đạt |
| R6 | Artifact = commit đã review (§1.1) | — | ❌ REL-B1 |
| R7 | Môi trường đích + vị trí dữ liệu được duyệt | `app/deploy/DATA_LOCATION.md`, OQ-005 | ⛔ chặn |
| R8 | Giám sát hoạt động trước khi mở cho người dùng | `docs/10-operations/dashboards.md` | ❌ chưa có Prometheus; metrics worker không được thu (OBS-1) |
| R9 | Rollback đã diễn tập trên môi trường đích | `rollback-plan.md` | ❌ mới diễn tập khôi phục CSDL cục bộ |
| R10 | Sao lưu ngay trước deploy | `app/deploy/backup.sh` | Chờ đến lúc deploy |

## 4. Feature flags

Ứng dụng **không có hệ thống flag lúc chạy**; các "công tắc" là biến môi trường, đổi cần khởi động lại cuốn chiếu từng bản api.

| Công tắc | Mặc định | Dùng khi phát hành |
|---|---|---|
| `LLM_PROVIDER` | `extractive` (AI giả, không gửi dữ liệu ra ngoài) | Giai đoạn 1 giữ `extractive`; chỉ đổi `http` khi OQ-005 + OQ-S01 được duyệt. **Đây là flag quan trọng nhất** — tắt về `extractive` là cách cắt dữ liệu ra ngoài nhanh nhất |
| `RAG_MIN_RELEVANCE` | `0.0` | Phải > 0 sau khi hiệu chỉnh (DEF-001) |
| `MAX_FILE_SIZE_MB`, `MAX_QUESTION_LENGTH` | trống | Phải có giá trị (OQ-009, OQ-P06, F-03) |
| `RATE_LIMIT_ENABLED` | `true` | Sản xuất sau proxy: `false` (proxy giới hạn) |
| `RETRIEVAL_MODE` | `exact` | Giữ `exact` tới ~40.000 đoạn (spike S3-00) |

## 5. Triển khai theo giai đoạn (staged rollout / canary)

Không có đăng nhập (CON-005) nên không chia người dùng theo tài khoản được; canary làm theo **allowlist mạng** (`deploy/proxy/allowlist.conf`) và theo **bản api**.

| Giai đoạn | Ai truy cập | Thời lượng tối thiểu | Tiếp tục khi | Dừng/rollback khi |
|---|---|---|---|---|
| 0. Khói | Nhóm dự án | 1 giờ | `make smoke` 17/17, `make proxy-test` 13/13 trên môi trường đích | Bất kỳ bước nào đỏ |
| 1. Canary bản api | Nhóm dự án; 1/2 bản api chạy phiên bản mới (nginx upstream) | 24 giờ | Mọi chỉ số trong dải kiểm soát (`docs/10-operations/dashboards.md` §2) | Ra khỏi dải ở chỉ số "đỏ" |
| 2. Thí điểm | 3–5 nhân viên kinh doanh (IP được thêm vào allowlist), `LLM_PROVIDER` theo quyết định OQ-005 | 1–2 tuần | Không sự cố Sev1/2; business owner đồng ý; bộ câu hỏi OQ-004 đạt | Sev1, hoặc câu trả lời bịa được xác nhận |
| 3. Toàn nhóm | Dải IP của nhóm kinh doanh | — | UAT G12 ký | — |

Việc triển khai cuốn chiếu từng bản api đã diễn tập cục bộ (`rolling-test.sh` 7/7).

## 6. Giám sát sau deploy

Theo dõi các chỉ số trong `docs/10-operations/dashboards.md` §2 **liên tục 1 giờ đầu**, rồi theo dải kiểm soát. Người trực: `[TBD: OQ-007]`.

## 7. Rollback

Xem `rollback-plan.md`. Tóm tắt: redeploy digest ảnh trước; lược đồ chỉ có migration 0001 nên không cần đảo migration; khôi phục CSDL chỉ khi dữ liệu hỏng.

## 8. Phê duyệt (người điền — agent không điền)

| Vai trò | Tên | Quyết định | Ngày |
|---|---|---|---|
| Release owner / người authorize deploy | `[TBD: OQ-007]` | ☐ Go ☐ No-go | |
| Người duyệt L2 | `[TBD]` | ☐ Đã approve mọi PR trong bản | |
| CNTT / bảo mật (G8, G9) | `[TBD: OQ-007]` | ☐ Chấp thuận ☐ Từ chối | |
| Business owner (G12) | `[TBD: OQ-007]` | ☐ Chấp thuận ☐ Từ chối | |

| Thời điểm deploy | Digest ảnh server | Digest ảnh web/proxy | Người thực hiện | Kết quả khói |
|---|---|---|---|---|
| | | | | |
