---
name: run-checks
description: Chạy kiểm tra chất lượng cho repo "Chat với tài liệu" (lint, kiểu, import-linter, unit/integration test, web tsc/vitest). Dùng trước khi commit/mở PR, hoặc khi người dùng nói "chạy test", "kiểm tra", "CI có xanh không".
---

# Chạy kiểm tra

Mọi lệnh `make` chạy từ thư mục `app/` (Makefile đang cố định đường dẫn Homebrew của macOS).

## Chọn mức kiểm tra

| Tình huống | Lệnh | Gồm |
|---|---|---|
| Vòng lặp nhanh khi đang code | `make check` | ruff + import-linter + unit test server + tsc/vitest web. **Không** có mypy, **không** có integration test |
| Chạm vào DB, API, worker, `schema.sql` | `make test-int` | integration test trên PostgreSQL thật (`cwd_test`) |
| Trước khi mở PR | `make ci` | Toàn bộ L0 như `.github/workflows/ci.yml`: thêm mypy, integration, coverage ≥ 70%, gitleaks, docker build. Log nằm ở `app/var/ci/` |
| Đổi hợp đồng API | `make contract` | Integration test + kiểm mọi phản hồi theo `docs/04-design/openapi.yaml` |
| Đổi prompt/retrieval/answer | `make eval` | Bộ đánh giá chất lượng trả lời (`eval_cwd`) — **không** thuộc L0, có ca đỏ có chủ đích |

## Chạy một test

```bash
cd app/server
.venv/bin/pytest tests/unit/test_adapters.py::test_name
.venv/bin/pytest -m integration tests/integration/test_flows.py::test_name   # cần DB
cd ../web && npx vitest run <tệp>
```

- `pytest` thường bỏ qua test `integration` (`addopts = "-q -m 'not integration'"`). CI dùng `-m "integration or not integration"`.
- Integration test **xóa và tạo lại** bảng `jobs`, `chunks`, `documents` trong `TEST_DATABASE_URL`. Tuyệt đối không trỏ vào CSDL có dữ liệu thật.
- Fixture PDF cần font DejaVu (hỗ trợ tiếng Việt); thiếu font thì test báo lỗi chứ không âm thầm in `?`.

## Khi báo kết quả

- Nói rõ đã chạy mức nào (`check` hay `ci`), mức nào chưa chạy và vì sao (ví dụ chưa có Docker/Colima nên `make ci` bỏ qua docker build).
- `make check` xanh **chưa** đủ chứng minh CI xanh. Nếu CI đỏ mà máy cục bộ xanh, dùng skill `reproduce-ci-failure`.
- Không hạ ngưỡng coverage (70%) hay thêm vào `.gitleaksignore` để cho qua.
