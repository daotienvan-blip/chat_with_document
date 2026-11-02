# Kết quả thực thi test case

Tạo lúc 2026-11-02 19:21 (UTC+7). Cấu trúc theo mẫu `test_reports/` của repo `unphuphu/Chat_With_AI`: mỗi test case có thư mục riêng `test_reports/<mã>_<tên>/` gồm `report.md`, `result.json` và `logs/`. Mã, mục tiêu và kết quả mong đợi của test case lấy từ [`docs/07-verification/test-plan.md`](../docs/07-verification/test-plan.md) (CWD-MTP-v1.0). Log của các bộ chạy chung nằm ở [`_logs/`](_logs/).

| Mục | Giá trị |
|---|---|
| Bản được kiểm | Mã `app/` không đổi suốt lượt chạy: là mã của `c6e849b` (bản sửa CI PyMuPDF), cũng là mã `app/` của `6014765` (`origin/main`). Commit `6014765` (19:09) chỉ thêm `CLAUDE.md` và `test_reports/`; CI trên GitHub chạy trên commit này |
| Ngày chạy | 2026-11-02, 18:49–19:16 (UTC+7) |
| Máy | macOS 27.2 (arm64), Python 3.12.16, PyMuPDF 1.28.2, Node v26.12.1 |
| AI | Chỉ AI giả trích xuất (`LLM_PROVIDER=extractive`); không dữ liệu nào được gửi tới dịch vụ AI bên ngoài |
| Người chạy | Agent (Claude) — không có quyền phê duyệt; kết quả cần QA Lead xem lại |

## Tổng hợp

| Kết luận | Số test case |
|---|---|
| ĐẠT | 29 |
| KHÔNG ĐẠT | 3 |
| CẦN NGƯỜI XÁC NHẬN | 7 |
| BỊ CHẶN | 15 |
| **Tổng** | **54** |

Test tự động trong lượt hồi quy: server 83 ca (53 đơn vị, 30 tích hợp) — 83 đạt, 0 lỗi, 0 bỏ qua; web 8 ca — 8 đạt, 0 lỗi. Coverage (L0): server 81,50% (câu lệnh + nhánh), web 80,55% dòng / 72,72% nhánh — cổng ≥ 70%.

## Lỗi phát hiện trong lượt này

| Mã | Mức (đề xuất) | Tóm tắt | Test case | Trạng thái |
|---|---|---|---|---|
| DEF-004 | Minor | Dừng một bản api trong lúc client đọc chậm tải tệp trực tiếp (không qua nginx): uvicorn thoát mã 0 sau khoảng 5 s, client không nhận đủ phản hồi và không nhận được FIN nên treo. Đường qua nginx (phần A) vẫn đạt. Mới thấy một lần; ngày 27/10 cùng bộ này đạt 7/7. Chẩn đoán: [reg04-rolling-b-chan-doan.txt](_logs/reg04-rolling-b-chan-doan.txt) | REG-04 | Mở — cần chạy lại phần B để biết có tái hiện ổn định không |
| DEF-005 | Minor | Proxy không gửi `Strict-Transport-Security` (HSTS) dù test plan SEC-05 yêu cầu. Proxy chỉ mở cổng TLS 8443 nên rủi ro hạ cấp xuống HTTP thấp | SEC-05 | Mở |
| DEF-006 | Major nếu G9 tính cả phụ thuộc dev; Minor nếu chỉ tính runtime — cần QA Lead quyết định | `npm audit`: 12 lỗ hổng trong phụ thuộc dev của web (8 moderate, 1 high, 3 critical; gồm tinypool, vitest, vite, esbuild, glob, minimatch). Phụ thuộc runtime: 0. `pip-audit` server: 0. Bản sửa cần nâng phiên bản chính (vitest 5, vite 8) | SEC-10 | Mở |

**Vấn đề của chính bộ kiểm thử** (không phải lỗi sản phẩm, nhưng làm kết quả kém tin cậy):

- `deploy/prod-local/rolling-test.sh` (phần B): client đọc chậm không đặt timeout, nên khi mất FIN cả bộ treo vô hạn; agent phải dừng client bằng tay sau hơn 5 phút.
- `deploy/proxy/proxy-test.sh` không kiểm HSTS dù SEC-05 yêu cầu, nên REG-04 vẫn 15/15 trong khi có DEF-005.
- `server/scripts/smoke.py` giả định kho tài liệu trống, so theo tên tệp, và tải 5 tệp liên tiếp vượt giới hạn tải lên của proxy (burst 3, 10/phút), nên chưa chạy được E2E-06 qua proxy.
- `server/scripts/spike_hnsw.py` cần CSDL đã migrate: số chiều lấy từ bảng `chunks`, tham số `--dim` không có tác dụng. Nạp 40.000 vector 384 chiều mất khoảng 7 phút.
- Số ca trong test-plan §6.7 đã cũ: REG-01 ghi 48 + 8, REG-02 ghi 29; lượt này có 53 + 8 và 30.
- Các lỗi mở từ trước trong `review-record.md` (ví dụ F-02: hàng đợi lặp khi worker chết) không có test case riêng nên không được kiểm lại trong lượt này.

## Chi tiết

| ID | Tiêu đề | Kết luận | Bước (đạt/tổng) | Log | Report |
|---|---|---|---|---|---|
| L0 | Cổng máy L0 (make ci) | ĐẠT | 12/12 | 3 | [report](L0_cong-may-l0-make-ci/report.md) |
| REG-01 | Hồi quy đơn vị server và web | ĐẠT | 61/61 | 2 | [report](REG-01_hoi-quy-don-vi-server-va-web/report.md) |
| REG-02 | Hồi quy tích hợp và hợp đồng API | ĐẠT | 30/30 | 3 | [report](REG-02_hoi-quy-tich-hop-va-hop-dong-api/report.md) |
| REG-03 | Khói đầu-cuối | ĐẠT | 17/17 | 3 | [report](REG-03_khoi-dau-cuoi/report.md) |
| REG-04 | Proxy và nâng cấp cuốn chiếu | KHÔNG ĐẠT | 21/22 | 4 | [report](REG-04_proxy-va-nang-cap-cuon-chieu/report.md) |
| REG-05 | Đánh giá AI G4, G5 | ĐẠT | 5/5 | 2 | [report](REG-05_danh-gia-ai-g4-g5/report.md) |
| API-01 | Tải lên tài liệu hợp lệ | ĐẠT | 1/1 | 1 | [report](API-01_tai-len-tai-lieu-hop-le/report.md) |
| API-02 | Tải lên bị từ chối | ĐẠT | 2/2 | 1 | [report](API-02_tai-len-bi-tu-choi/report.md) |
| API-03 | Tải lên nguyên tử khi kho hoặc CSDL lỗi | ĐẠT | 1/1 | 1 | [report](API-03_tai-len-nguyen-tu-khi-kho-hoac-csdl-loi/report.md) |
| API-04 | Danh sách tài liệu | ĐẠT | 1/1 | 1 | [report](API-04_danh-sach-tai-lieu/report.md) |
| API-05 | Tải tệp gốc | ĐẠT | 1/1 | 1 | [report](API-05_tai-tep-goc/report.md) |
| API-06 | Xóa tài liệu bất biến | ĐẠT | 1/1 | 1 | [report](API-06_xoa-tai-lieu-bat-bien/report.md) |
| API-07 | Hỏi có căn cứ kèm nguồn | ĐẠT | 1/1 | 1 | [report](API-07_hoi-co-can-cu-kem-nguon/report.md) |
| API-08 | Câu hỏi không hợp lệ | ĐẠT | 1/1 | 1 | [report](API-08_cau-hoi-khong-hop-le/report.md) |
| API-09 | Lỗi dịch vụ AI | ĐẠT | 1/1 | 1 | [report](API-09_loi-dich-vu-ai/report.md) |
| API-10 | Chịu tải | ĐẠT | 1/1 | 1 | [report](API-10_chiu-tai/report.md) |
| API-11 | readyz với vai trò tối thiểu | ĐẠT | 1/1 | 1 | [report](API-11_readyz-voi-vai-tro-toi-thieu/report.md) |
| E2E-01 | Tải, chờ sẵn sàng, hỏi | CẦN NGƯỜI XÁC NHẬN | 6/7 | 1 | [report](E2E-01_tai-cho-san-sang-hoi/report.md) |
| E2E-02 | Hỏi trên nhiều tài liệu | CẦN NGƯỜI XÁC NHẬN | 3/4 | 1 | [report](E2E-02_hoi-tren-nhieu-tai-lieu/report.md) |
| E2E-03 | Câu hỏi ngoài tài liệu | CẦN NGƯỜI XÁC NHẬN | 2/3 | 1 | [report](E2E-03_cau-hoi-ngoai-tai-lieu/report.md) |
| E2E-04 | Tệp lỗi | CẦN NGƯỜI XÁC NHẬN | 3/4 | 1 | [report](E2E-04_tep-loi/report.md) |
| E2E-05 | Xóa tài liệu rồi hỏi lại | CẦN NGƯỜI XÁC NHẬN | 3/4 | 1 | [report](E2E-05_xoa-tai-lieu-roi-hoi-lai/report.md) |
| E2E-06 | Lặp E2E qua proxy TLS | BỊ CHẶN | 1/2 | 1 | [report](E2E-06_lap-e2e-qua-proxy-tls/report.md) |
| E2E-07 | Dùng trên điện thoại | BỊ CHẶN | 0/1 | 0 | [report](E2E-07_dung-tren-dien-thoai/report.md) |
| UAT-01 | Người dùng tự tải tài liệu thật | BỊ CHẶN | 0/1 | 0 | [report](UAT-01_nguoi-dung-tu-tai-tai-lieu-that/report.md) |
| UAT-02 | Hai mươi câu hỏi thật | BỊ CHẶN | 0/1 | 0 | [report](UAT-02_hai-muoi-cau-hoi-that/report.md) |
| UAT-03 | Câu ngoài tài liệu do người dùng đặt | BỊ CHẶN | 0/1 | 0 | [report](UAT-03_cau-ngoai-tai-lieu-do-nguoi-dung-dat/report.md) |
| UAT-04 | Câu hỏi cần ghép nhiều tài liệu | BỊ CHẶN | 0/1 | 0 | [report](UAT-04_cau-hoi-can-ghep-nhieu-tai-lieu/report.md) |
| UAT-05 | Số thao tác so với cách thủ công | BỊ CHẶN | 0/1 | 0 | [report](UAT-05_so-thao-tac-so-voi-cach-thu-cong/report.md) |
| PERF-01 | Độ trễ truy xuất vector | ĐẠT | 2/2 | 1 | [report](PERF-01_do-tre-truy-xuat-vector/report.md) |
| PERF-02 | Tải tệp lớn trong lúc nâng cấp | ĐẠT | 3/3 | 1 | [report](PERF-02_tai-tep-lon-trong-luc-nang-cap/report.md) |
| PERF-03 | Người dùng đồng thời | BỊ CHẶN | 0/1 | 0 | [report](PERF-03_nguoi-dung-dong-thoi/report.md) |
| PERF-04 | Thời gian tài liệu sẵn sàng | BỊ CHẶN | 0/1 | 1 | [report](PERF-04_thoi-gian-tai-lieu-san-sang/report.md) |
| PERF-05 | Thời gian build CI | ĐẠT | 2/2 | 2 | [report](PERF-05_thoi-gian-build-ci/report.md) |
| SEC-01 | Tệp tải lên không tin cậy | ĐẠT | 18/18 | 1 | [report](SEC-01_tep-tai-len-khong-tin-cay/report.md) |
| SEC-02 | Chống injection | ĐẠT | 5/5 | 1 | [report](SEC-02_chong-injection/report.md) |
| SEC-03 | Phân quyền CSDL tối thiểu | ĐẠT | 2/2 | 1 | [report](SEC-03_phan-quyen-csdl-toi-thieu/report.md) |
| SEC-04 | Không lộ nội dung | ĐẠT | 1/1 | 1 | [report](SEC-04_khong-lo-noi-dung/report.md) |
| SEC-05 | Bảo mật truyền tải | KHÔNG ĐẠT | 6/7 | 2 | [report](SEC-05_bao-mat-truyen-tai/report.md) |
| SEC-06 | Kiểm soát truy cập mạng | ĐẠT | 2/2 | 1 | [report](SEC-06_kiem-soat-truy-cap-mang/report.md) |
| SEC-07 | Bí mật | ĐẠT | 2/2 | 2 | [report](SEC-07_bi-mat/report.md) |
| SEC-08 | Cấu hình container | ĐẠT | 1/1 | 1 | [report](SEC-08_cau-hinh-container/report.md) |
| SEC-09 | Chống lạm dụng tài nguyên | ĐẠT | 6/6 | 2 | [report](SEC-09_chong-lam-dung-tai-nguyen/report.md) |
| SEC-10 | Quét lỗ hổng phụ thuộc và ảnh | KHÔNG ĐẠT | 2/4 | 4 | [report](SEC-10_quet-lo-hong-phu-thuoc-va-anh/report.md) |
| ACC-01 | Dùng bằng bàn phím | BỊ CHẶN | 0/1 | 0 | [report](ACC-01_dung-bang-ban-phim/report.md) |
| ACC-02 | Trình đọc màn hình | BỊ CHẶN | 0/1 | 0 | [report](ACC-02_trinh-doc-man-hinh/report.md) |
| ACC-03 | Độ tương phản | BỊ CHẶN | 0/1 | 0 | [report](ACC-03_do-tuong-phan/report.md) |
| ACC-04 | Thuộc tính ARIA | BỊ CHẶN | 0/1 | 0 | [report](ACC-04_thuoc-tinh-aria/report.md) |
| ACC-05 | Quản lý focus | CẦN NGƯỜI XÁC NHẬN | 1/2 | 1 | [report](ACC-05_quan-ly-focus/report.md) |
| ACC-06 | Thông báo lỗi không chỉ bằng màu | ĐẠT | 2/2 | 1 | [report](ACC-06_thong-bao-loi-khong-chi-bang-mau/report.md) |
| UI-01 | So sánh với thiết kế | BỊ CHẶN | 0/1 | 0 | [report](UI-01_so-sanh-voi-thiet-ke/report.md) |
| UI-02 | Đáp ứng 320 đến 1440 px | BỊ CHẶN | 0/1 | 0 | [report](UI-02_dap-ung-320-den-1440-px/report.md) |
| UI-03 | Trạng thái thành phần | CẦN NGƯỜI XÁC NHẬN | 5/6 | 1 | [report](UI-03_trang-thai-thanh-phan/report.md) |
| UI-04 | Ánh xạ lỗi | ĐẠT | 1/1 | 1 | [report](UI-04_anh-xa-loi/report.md) |

## Truy vết tiêu chí chấp nhận

Ghép marker `@pytest.mark.req` và tên test web `[US-xxx-ACn]` với kết quả JUnit của REG-01 và REG-02.

| AC | Số ca test | Kết quả |
|---|---|---|
| US-001-AC1 | 1 | ✅ Đạt |
| US-001-AC2 | 2 | ✅ Đạt |
| US-001-AC3 | 5 | ✅ Đạt |
| US-002-AC1 | 4 | ✅ Đạt |
| US-002-AC2 | 2 | ✅ Đạt |
| US-003-AC1 | 5 | ✅ Đạt |
| US-003-AC2 | 6 | ✅ Đạt |
| US-003-AC3 | 5 | ✅ Đạt |
| US-003-AC4 | 1 | ✅ Đạt |
| US-004-AC1 | 1 | ✅ Đạt |
| US-005-AC1 | 2 | ✅ Đạt |
| US-005-AC2 | 1 | ✅ Đạt |
| US-006-AC1 | 2 | ✅ Đạt |
| US-006-AC2 | 1 | ✅ Đạt |
| US-006-AC3 | 1 | ✅ Đạt |
| US-007-AC1 | 2 | ✅ Đạt |
| US-007-AC2 | 1 | ✅ Đạt |
| US-008-AC1 | 2 | ✅ Đạt |
| US-009-AC1 | 1 | ✅ Đạt |
| US-009-AC2 | 1 | ✅ Đạt |
| US-010-AC1 | 10 | ✅ Đạt |
| US-010-AC2 | 2 | ✅ Đạt |
| US-015-AC1 | 0 | ⛔ Chỉ có bằng chứng tài liệu (`deploy/DATA_LOCATION.md`), chờ OQ-005 |

`make trace`: 22/23 AC có test; US-015-AC1 chỉ có bằng chứng ngoài mã ([trace.txt](_logs/trace.txt)).

## Khác với mẫu tham chiếu

- Không có ảnh chụp màn hình và video. Mẫu quay bằng Playwright; dự án này chưa có Playwright (S8-08). Bằng chứng là log văn bản và JUnit XML trong `logs/` của từng test case; dòng đầu mỗi log là lệnh đã chạy, có thể chạy lại nguyên văn.
- Mã test case theo `test-plan.md` của dự án (API-01, E2E-01, SEC-01…), không theo mã của mẫu (API-001…). Có thêm L0 và REG-01…05 vì kế hoạch định nghĩa chúng.
- Các bộ chạy chung (L0, REG-03, REG-04, REG-05, PERF-01) chạy một lần; các test case dùng kết quả của chúng (E2E-01…06, PERF-02/04/05, SEC-05/06/09) trỏ về log trong `_logs/`.
- Bước cần trình duyệt thật được ghi "Cần người xác nhận"; test case không chạy được bước nào được ghi "Bị chặn" kèm lý do. Có thêm kết luận KHÔNG ĐẠT, vì mẫu không có trường hợp này.
- Chưa có `_archive/` vì đây là lượt đầu theo cấu trúc này. Lượt sau nên chuyển thư mục cũ vào `_archive/<mã>__<thời điểm>/` như mẫu.

## Môi trường đã dựng và trạng thái sau khi chạy

- Đã bật PostgreSQL 17 (Homebrew), Colima, stack dev (`make up`, cho 2 test adapter S3) và stack prod cục bộ (`make prod-up`, ảnh build từ mã đang kiểm). Sau khi chạy đã tắt lại cả bốn; các volume dữ liệu `cwd-dev_*` và `cwd-prod_*` được giữ nguyên.
- CSDL tạm `cwd_smoke` (REG-03) và `cwd_spike` (PERF-01) được tạo riêng và đã xóa sau khi chạy. Các bộ test xóa và tạo lại dữ liệu trong `cwd_test` như thường lệ. CSDL demo `cwd` không bị đụng tới.
- Tệp thử 21 MB của REG-04 đã được xóa khỏi stack prod (DELETE 204, sau đó GET 404). Stack prod vẫn còn 7 tài liệu từ các lượt chạy trước hôm nay.
- Chỉ dùng AI giả trích xuất. Kết nối ra ngoài trong lượt này: `npm audit` (registry npm), `pip-audit` (PyPI), GitHub API công khai (đọc kết quả CI).

## Phê duyệt

| Vai trò | Họ tên | Quyết định | Ngày |
|---|---|---|---|
| QA Lead | | ☐ Chấp nhận ☐ Yêu cầu bổ sung | |
| Product owner | | ☐ Chấp nhận ☐ Yêu cầu bổ sung | |
