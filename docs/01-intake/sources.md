# Sources — "Chat với tài liệu" (MVP)

> **Mục đích:** liệt kê nguồn dữ liệu và tài liệu làm đầu vào cho intake. Mỗi nguồn ghi vị trí, phiên bản, và trạng thái xác thực.
> **Ngày rà soát:** 2026-10-26

## Nguồn bối cảnh và yêu cầu

| ID | Nguồn | Vị trí | Phiên bản | Trạng thái | Ghi chú |
|---|---|---|---|---|---|
| SRC-001 | Bối cảnh và yêu cầu từ quản lý ("BRD_Prompt_IEEE_standard.md") | `~/Downloads/BRD_Prompt_IEEE_standard.md` (ngoài thư mục dự án) | 1.0 | Tìm thấy, chưa đối chiếu | Không nằm trong `chat_with_document/`. Nên chuyển vào `docs/01-intake/` để tài liệu tự đủ nguồn. |
| REF-001 | IEEE 29148-2018 | IEEE | 2018 | Tham chiếu chuẩn | Khung của BRD và PRD |
| REF-002 | IEEE 1016-2009 | IEEE | 2009 | Tham chiếu chuẩn | Khung của SDD và SADD |

## Tài liệu đã tạo trong dự án

| ID | Tài liệu | Vị trí | Phiên bản |
|---|---|---|---|
| DOC-01 | BRD | `docs/02-requirements/BRD.md` | 0.6 |
| DOC-02 | PRD | `docs/03-analysis/PRD.md` | 0.6 |
| DOC-03 | Sơ đồ use case | `docs/diagrams/use-case-diagram.drawio` | 13 UC, 1 actor người, 2 actor hệ thống; trang 2 là danh mục |
| DOC-04 | SDD (Blueprint Design) | `docs/04-design/Blueprint_Design.md` | 0.1 (Draft); thay bản cũ ở `docs/design/` (không còn trong repo) |
| DOC-05 | SAD (Software Architecture Design) | `docs/04-design/SAD.md` | 0.1 (Draft); thay SADD cũ (`docs/design/SADD.md`, không còn trong repo) |
| DOC-06 | UIUX Blueprint Design | `docs/design/UIUX_Blueprint_Design.md` | Không còn trong repo (kiểm tra 2026-10-27) |
| DOC-07 | Thiết kế màn hình HTML | `docs/design/html_design/` | Không còn trong repo (kiểm tra 2026-10-27) |
| DOC-09 | API Design + đặc tả OpenAPI | `docs/04-design/API_Design.md`, `docs/04-design/openapi.yaml` | 0.1 (Draft); OpenAPI 3.0 đã kiểm hợp lệ |
| DOC-10 | Database Design + DDL | `docs/04-design/Database_Design.md`, `docs/04-design/schema.sql` | 0.1 (Draft); DDL đã kiểm cú pháp, chưa chạy trên máy chủ thật |
| DOC-11 | Thiết kế màn hình HTML | `docs/04-design/html_design/` | 0.1 (Draft); 6 màn hình + trang danh mục `index.html`, mỗi màn hình một tệp độc lập; chưa mở trong trình duyệt thật |
| DOC-08 | Checklist BRD / PRD / SAD | `docs/02-requirements/` (BRD), `docs/03-analysis/` (PRD), `docs/04-design/` (SAD), `*_Checklist.xlsx` | — |

## Dữ liệu dự kiến (chưa có)

| ID | Dữ liệu | Trạng thái | Chặn |
|---|---|---|---|
| DATA-01 | Bộ tài liệu PDF mẫu (không nhạy cảm) | Chưa có | Spike S1, bộ đánh giá PLT-4, cổng G3–G5 (DEP-002) |
| DATA-02 | Bộ câu hỏi kiểm thử và đáp án, do business owner xác nhận | Chưa có | MET-002, cổng G3 (OQ-004) |
| DATA-03 | Số liệu baseline thời gian tra cứu | Chưa có | MET-001 (OQ-001) |
| DATA-04 | Số tài liệu, kích thước, tỷ lệ PDF ảnh quét trong thực tế | Chưa có | RSK-005, ASM-001, NFR-CAP-001 (OQ-009, OQ-014) |
| DATA-05 | Hệ thống hoặc kho tài liệu hiện có liên quan | Chưa rõ | DEP-004 (OQ-014) |

## Quyết định về nguồn

- Mọi số liệu trong intent đều có nguồn trong danh sách trên, hoặc được đánh dấu `[TBD]` / `[Unverified]`.
- Trước khi PO phê duyệt intent, cần đối chiếu nội dung SRC-001 với BRD và chuyển tệp vào dự án.
