# Báo cáo coverage — 2026-10-28

Lượt chạy: `make ci` trên `ec18ff6` + thay đổi giai đoạn 7 (log: `ci.log`). Cổng L0: **≥ 70%** (test-plan §6.3).

## Server (coverage.py, unit + tích hợp, 77 test)

| Chỉ số | Giá trị | Cổng |
|---|---|---|
| Tổng (câu lệnh + nhánh) — chỉ số dùng cho cổng | **83%** | ✅ ≥ 70% |
| Dòng | 85.3% | — |
| Nhánh | 69.1% | (tham khảo) |

Loại trừ: `persistence/migrations/*`, `api/main.py` (điểm khởi động uvicorn, được kiểm bằng `make smoke`). Chi tiết theo tệp: `server-coverage.txt`; XML (Cobertura): `server-coverage.xml`; HTML: `app/var/ci/server-htmlcov/` (không commit).

**Vùng coverage thấp — đã xem xét:**

| Tệp | Coverage | Lý do / hành động |
|---|---|---|
| `platform/logging.py` | 28% | Formatter JSON được kiểm gián tiếp qua `test_observability_no_content_leak` (bắt bản ghi, không qua handler) → nên thêm test định dạng |
| `worker/__main__.py` | 37% | Vòng chính + xử lý tín hiệu; kiểm bằng `rolling-test.sh` (dừng êm, exit 0) ngoài pytest |
| `adapters/pymupdf_extractor.py` | 49% | Phần chạy trong tiến trình con không được coverage đo; hành vi được kiểm bằng `test_pdf_extractor_cases` |
| `adapters/stores.py` | 55% | `LocalFsObjectStore` chỉ kiểm qua smoke/demo → nên thêm test đơn vị (range, xóa, tên khóa) |
| `worker/runner.py` | 74% | Nhánh `release_overdue` → thất bại khi vượt số lần chưa có (liên quan F-02 trong `review-record.md`) |

## Web (vitest + v8, 8 test)

| Chỉ số | Giá trị | Cổng |
|---|---|---|
| Dòng | **80.55%** (518/643) | ✅ |
| Câu lệnh | 80.55% | ✅ |
| Nhánh | 72.72% (168/231) | ✅ |
| Hàm | 77.35% (41/53) | ✅ |

Loại trừ: `src/api-client/generated.ts` (chỉ khai báo kiểu), tệp test. Tệp JSON: `web-coverage-summary.json`.
