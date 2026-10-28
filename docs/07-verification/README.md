# 07 — Kiểm chứng & Phê duyệt (Verify & Review)

Trạng thái ngày 2026-10-28: **L0 xanh · L1 xong · L2/L3/L4 chờ người.** Chưa đủ điều kiện phát hành (DEF-001 làm G5 không đạt).

| Tầng | Trạng thái | Bằng chứng |
|---|---|---|
| L0 — CI (lint, kiểu, test, coverage ≥ 70%, quét bí mật, build < 10 phút) | ✅ Xanh cục bộ (`make ci`, 137 s); workflow GitHub chưa chạy lần đầu | `evidence/ci.log`, `.github/workflows/ci.yml` |
| L1 — Agent review (rubric + IEEE 1028, trích dòng) | ✅ Xong — 14 phát hiện (3 Major), RO-1 13/14, RO-2 10/14 | `review-record.md`, `Code_Review_IEEE_1028_Checklist.xlsx` |
| L2 — Người duyệt (≠ tác giả, PR ≤ 400 dòng, đọc diff) | ⏳ Chờ — **chưa chỉ định người duyệt** (2026-10-28) | `review-record.md` §8, `l2-reviewer-guide.md`, `pr-description.md` |
| L3 — Inspection vùng rủi ro cao | ⏳ Chờ | `review-record.md` §7 |
| L4 — Xác nhận với stakeholder / UAT | ⛔ Chặn bởi OQ-004, OQ-005 | `test-plan.md` §6.6 |

## Tệp

| Tệp | Nội dung |
|---|---|
| `test-plan.md` | Master Test Plan IEEE 829 (CWD-MTP-v1.0) + ma trận truy vết AC → test |
| `Test_Plan_IEEE_829_Checklist.xlsx` | Checklist IEEE 829 đã điền (15 Done, 3 In Progress) |
| `test-report.md` | Báo cáo tổng kết kiểm thử, lỗi DEF-001…003, trạng thái cổng |
| `review-record.md` | Biên bản review L1, rubric 7 tiêu chí, kế hoạch L2/L3/L4, bảng ký L2 |
| `Code_Review_IEEE_1028_Checklist.xlsx` | Checklist IEEE 1028 đã điền (13 Pass, 6 Fail) |
| `l2-reviewer-guide.md` | Gói giao cho người duyệt L2: điều kiện, thứ tự, cách chấm rubric 0/1/2, cách ghi kết quả |
| `pr-description.md` | Mô tả PR cho thay đổi giai đoạn 7 |
| `evidence/` | `ci.log`, coverage (txt/xml/json + `coverage-summary.md`), `smoke.log`, `proxy-test.log`, `eval-report.md` |

## Chạy lại

```bash
cd app
make ci          # L0 cục bộ → var/ci/
make smoke       # cần hệ thống đang chạy (make demo)
make eval        # G4/G5 — q15 hiện đỏ (DEF-001)
make proxy-test  # cần make prod-up
```
