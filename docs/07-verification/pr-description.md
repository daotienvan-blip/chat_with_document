# Giai đoạn 7: CI L0 (lint, kiểu, test, coverage ≥ 70%, quét bí mật, build) + sửa lỗi kiểu

> Bản nháp mô tả PR cho RO-1 (`review-record.md`). Nhánh đề xuất: `verify/phase-7-ci`. Tác giả tạo PR; **approver phải khác tác giả**; agent không approve/merge.

## Tóm tắt

- Thêm workflow `.github/workflows/ci.yml`: 4 job song song (server, web, secrets, images), mỗi job ≤ 10 phút, `permissions: contents: read`.
- Thêm `make ci` (`app/deploy/ci-local.sh`) chạy đúng các bước của workflow trên máy, ghi log và coverage vào `app/var/ci/`.
- Bật **mypy** (lần đầu) và sửa 8 lỗi kiểu, gồm 1 lỗi thật: middleware giới hạn tốc độ bắt `Exception` rồi đọc `e.code` (AttributeError nếu bộ giới hạn ném lỗi khác) → thu hẹp thành `except RateLimited`.
- Ngưỡng coverage 70% đặt trong cấu hình công cụ (`pyproject.toml` `fail_under`, `vite.config.ts` `thresholds`).
- gitleaks quét toàn bộ lịch sử git, tải bản phát hành có kiểm SHA-256; 1 báo nhầm ghi trong `.gitleaksignore`.
- Thêm ca hồi quy `q15` vào bộ đánh giá cho DEF-001 (ca này **đang đỏ có chủ đích** — `make eval` không thuộc L0).
- Hồ sơ xác minh: `docs/07-verification/`.

## Kết quả L0 (cục bộ, `make ci`)

```
::: PASS ruff · mypy · import-linter
::: PASS pytest unit+tích hợp, coverage ≥ 70%   (77 test, 83%)
::: PASS tsc · vitest + coverage ≥ 70%           (8 test, 80.6% dòng)
::: PASS vite build · gitleaks (lịch sử git) · docker build server · docker build web
::: tổng thời gian 137s (giới hạn 600s)
::: L0 XANH
```

## Người duyệt cần kiểm

- [ ] Lượt CI đầu tiên trên GitHub: cả 4 job xanh, mỗi job < 10 phút.
- [ ] Job `server` dùng service `pgvector/pgvector:pg17` — test tích hợp thật sự chạy (không bị bỏ qua): 29 test có marker `integration`.
- [ ] Các sửa kiểu ở `retrieval/service.py`, `validate_upload.py`, `runner.py`, `pymupdf_extractor.py` không đổi hành vi.
- [ ] Không hạ ngưỡng coverage; `.gitleaksignore` chỉ chứa đúng 1 dấu vân tay đã giải thích.
- [ ] Sau khi merge: bật bảo vệ nhánh `main` — bắt buộc check `ci` + 1 approval, cấm push trực tiếp.

## Ngoài phạm vi PR này

DEF-001 / F-01, F-02, F-03 (Major) — mỗi lỗi một PR riêng kèm ca hồi quy (`review-record.md` §4).

## Truy vết

`test-plan.md` §6.1 (L0), §7 (tiêu chí); `test-report.md` §7 (danh sách tệp); `review-record.md` F-13, F-14.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
