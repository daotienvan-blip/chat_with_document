# Test report – L0: Cổng máy L0 (make ci)

| Trường | Giá trị |
|---|---|
| Test case | [L0](../../docs/07-verification/test-plan.md) — `test-plan.md` §6.1, §7 |
| Kết luận | **ĐẠT** |
| Bắt đầu | 2026-11-02T11:49:31.000Z |
| Kết thúc | 2026-11-02T11:49:51.000Z (20.0 s) |
| Cách thực hiện | Tự động – `make ci` (`app/deploy/ci-local.sh`, cùng các bước với `.github/workflows/ci.yml`) và GitHub Actions |
| URL ứng dụng | — |
| Bản build | `6014765` (`origin/main`); mã trong `app/` giống hệt `c6e849b` — commit `6014765` chỉ thêm `CLAUDE.md` và `test_reports/`; không có thay đổi chưa commit trong `app/` |
| Máy chạy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| CSDL | PostgreSQL 17.11 (Homebrew) + pgvector 0.8.7; stack Docker dùng ảnh `pgvector/pgvector:pg17` |
| Docker | Colima, Docker 29.5.2 |
| Trình duyệt | Không dùng — test web chạy trên jsdom (vitest); dự án chưa có Playwright (S8-08) |

## Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| 1 | ruff | Không có lỗi lint | All checks passed! | Đạt | [log](../_logs/l0-ci.log) |
| 2 | mypy | Không có lỗi kiểu | Không lỗi trong 46 tệp nguồn | Đạt | [log](../_logs/l0-ci.log) |
| 3 | import-linter | Mọi hợp đồng phụ thuộc giữ | 3 giữ, 0 vỡ | Đạt | [log](../_logs/l0-ci.log) |
| 4 | pytest unit+tích hợp, coverage ≥ 70% | 100% test đạt; coverage ≥ 70% | 81 đạt, 2 bỏ qua (2 test S3: runner không có SeaweedFS — đã chạy ở REG-02); coverage 81.50% | Đạt | [log](../_logs/l0-ci.log) |
| 5 | tsc | Không có lỗi kiểu | Không lỗi | Đạt | [log](../_logs/l0-ci.log) |
| 6 | vitest + coverage ≥ 70% | 100% test đạt; coverage ≥ 70% | 8/8 đạt; dòng 80.55% | Đạt | [log](../_logs/l0-ci.log) |
| 7 | vite build | Build thành công | Build thành công | Đạt | [log](../_logs/l0-ci.log) |
| 8 | gitleaks (lịch sử git) | 0 bí mật | no leaks found (12 commit) | Đạt | [log](../_logs/l0-ci.log) |
| 9 | docker build server | Build ảnh thành công | sha256:c3cd71a921d5… | Đạt | [log](../_logs/l0-ci.log) |
| 10 | docker build web | Build ảnh thành công | sha256:5e81e4feed3a… | Đạt | [log](../_logs/l0-ci.log) |
| 11 | Tổng thời gian L0 | ≤ 600 s | 20 s | Đạt | [log](../_logs/l0-ci.log) |
| 12 | CI trên GitHub Actions (ubuntu-24.04 x86_64), commit `6014765` | 4/4 job xanh | 4/4 job success — secret scan (gitleaks), server · lint + type + test + coverage, web · type + test + coverage, build ảnh Docker | Đạt | [log](../_logs/l0-github-actions.json) |

## Log

- [l0-ci.log](../_logs/l0-ci.log)
- [l0-server-junit.xml](../_logs/l0-server-junit.xml)
- [l0-github-actions.json](../_logs/l0-github-actions.json)

## Ghi chú / lỗi phát hiện

- Bước 1–11: L0 cục bộ trên macOS arm64, chạy trên `c6e849b` lúc 18:49 (UTC+7). Bước 12: CI trên GitHub cho `6014765` (https://github.com/daotienvan-blip/chat_with_document/actions/runs/41442350109), có cùng mã `app/`.
- `6014765` được push thẳng lên `main` lúc 19:09 (UTC+7), không qua pull request. Đây là lượt CI xanh đầu tiên trên `main` sau sự cố PyMuPDF 2.0 (INC-2026-10-28-01).
- Build ảnh Docker cục bộ dùng lại lớp cache từ lần build trước cùng mã nguồn, nên mất 0–1 s.
