# Intent — "Chat với tài liệu" (MVP)

> **Trạng thái:** Draft, **chờ PO phê duyệt** (bước 4)
> **Nguồn:** `docs/02-requirements/BRD.md` (v0.6), `docs/03-analysis/PRD.md` (v0.6)
> **Ngôn ngữ:** Tiếng Việt
> **Quy ước:** `[TBD: OQ-xxx]` = chưa có thông tin. `[Đề xuất]` = chưa được xác nhận. `[Unverified]` = chưa có nguồn.

---

## 1. Problem

Nhân viên phát triển kinh doanh làm việc với nhiều tài liệu PDF nhưng khó nắm đầy đủ nội dung. Mỗi lần cần một thông tin, họ phải mở và tổng hợp thủ công từ nhiều file, tốn thời gian (BRD §2, SRC-001). Mức thiệt hại định lượng (giờ công, chi phí) **chưa có số liệu** `[TBD: OQ-001]`.

## 2. Proposed outcome

Một ứng dụng web cho phép tải PDF lên, đặt câu hỏi bằng ngôn ngữ tự nhiên, và nhận câu trả lời dựa trên nội dung các tài liệu đã tải, kèm nguồn (tên tài liệu, số trang) để kiểm chứng. Nếu tài liệu không có thông tin, hệ thống nói rõ là không tìm thấy thay vì bịa.

MVP chỉ giữ luồng cốt lõi: *tải PDF → hỏi → câu trả lời có nguồn hoặc "không tìm thấy"*. Mục đích là kiểm chứng giá trị trước khi đầu tư mở rộng.

### 2.1 Phạm vi use case (theo sơ đồ)

Sơ đồ có 13 use case trong 2 nhóm, một actor người và hai hệ thống ngoài:

| Nhóm | Use case | Nội dung |
|---|---|---|
| B. Quản lý tài liệu | UC07 Tải PDF lên (include UC08, UC09; extend UC10) · UC11 Xem danh sách · UC12 Xóa tài liệu | Luồng tải, theo dõi trạng thái và xóa |
| C. Hỏi đáp trên tài liệu | UC14 Đặt câu hỏi (include UC15, UC21; extend UC18, UC19) · UC15 Hiển thị nguồn (extend UC16, UC17) | Luồng hỏi đáp có trích nguồn |

Actor: Người dùng kinh doanh (người); Kho lưu trữ tài liệu IF-03; Dịch vụ AI IF-02. Không có use case quản trị, đăng nhập, nhật ký, số liệu, hỏi tiếp nối hay chia sẻ.

## 3. Affected users

| Nhóm | Vai trò | Nguồn |
|---|---|---|
| Nhân viên phát triển kinh doanh (UC-P1) | Người dùng chính | BRD §6.1 |
| Trưởng nhóm / quản lý kinh doanh (UC-P2) | Người dùng phụ, cần tổng hợp và kiểm chứng nguồn | `[Unverified]` |

Bên liên quan không phải người dùng trực tiếp: quản lý/sponsor (STK-002), CNTT/bảo mật (STK-003), chủ sở hữu tài liệu (STK-004), nhà cung cấp AI (STK-006). Ngoài ra, hai hệ thống ngoài (IF-02, IF-03) là actor trong sơ đồ use case. Chi tiết ở `stakeholders.md`.

## 4. Constraints

| ID | Ràng buộc |
|---|---|
| CON-001 | Sản phẩm là ứng dụng web; hỗ trợ trình duyệt máy tính |
| CON-002 | Đầu vào là PDF có văn bản trích xuất được; không OCR trong MVP |
| CON-003 | Ngân sách và mốc thời gian `[TBD: OQ-003]` |
| CON-004 | Yêu cầu pháp lý/tuân thủ về dữ liệu `[TBD: OQ-005]` |
| CON-005 | **Không có đăng nhập:** mọi người truy cập dùng chung một kho tài liệu. Chỉ triển khai trong mạng nội bộ/VPN và chỉ với tài liệu mọi người được phép xem, tới khi OQ-005 đóng |

Phạm vi bị ràng buộc bởi CON-005: không có phân quyền, cô lập dữ liệu theo người dùng, hay nhật ký truy cập ở MVP.

## 5. Success measures

| Metric | Định nghĩa (rút gọn) | Baseline | Target |
|---|---|---|---|
| MET-001 | Thời gian trung bình để tìm được một thông tin đúng | `[TBD: OQ-001]` | `[TBD: OQ-002]` |
| MET-002 | Tỷ lệ câu trả lời đúng và có nguồn hợp lệ trên bộ câu hỏi kiểm thử | `[TBD: OQ-001]` | `[TBD: OQ-004]` (đề xuất ≥ 85%) |

Trạng thái sẵn sàng phê duyệt: **Not ready**. Các OQ chặn: OQ-001, OQ-002, OQ-003, OQ-004, OQ-005, OQ-007.

## 6. Out of scope

- Định dạng khác PDF; OCR cho PDF ảnh quét.
- Ứng dụng di động gốc.
- Tích hợp CRM/ERP/kho tài liệu doanh nghiệp; chỉnh sửa tài liệu gốc.
- Đăng nhập, phân quyền, cô lập dữ liệu theo người dùng, chia sẻ tài liệu, nhật ký truy cập, giao diện quản trị, bảng số liệu, hỏi tiếp nối theo ngữ cảnh, cam kết thời gian phản hồi và SLA.

## 7. Open questions

| ID | Câu hỏi | Chủ sở hữu |
|---|---|---|
| OQ-001 | Baseline: thời gian tra cứu, số tài liệu, số người dùng | `[TBD]` |
| OQ-002 | Target cho MET-001 | Sponsor |
| OQ-003 | Ngân sách, mốc thời gian, tác nhân kích hoạt | Sponsor |
| OQ-004 | Ngưỡng độ chính xác; ai xác nhận bộ câu hỏi kiểm thử | Business owner |
| OQ-005 | Độ nhạy cảm tài liệu, nơi lưu trữ, thời hạn lưu giữ, có gửi nội dung tới AI bên ngoài không | CNTT/Bảo mật/Pháp lý |
| OQ-007 | Ai là sponsor, business owner, product owner, approver | Quản lý |
| OQ-011 | Ngôn ngữ tài liệu và câu hỏi | Business owner |

Mô hình truy cập: dùng chung một kho, không đăng nhập (CON-005). Cần CNTT/bảo mật chấp nhận qua OQ-005.

---

## 8. Owner, acceptance criteria, risk tier (bước 4 — để PO điền)

| Mục | Đề xuất | Quyết định của PO |
|---|---|---|
| Owner | `[TBD: OQ-007]` | |
| Acceptance criteria | Xem BRD §11 (AC-001 … AC-018) và `03-analysis/USER_STORIES.md` | |
| Risk tier | **High `[Đề xuất]`** — lý do: không có đăng nhập và sensitivity tài liệu chưa rõ (RSK-002, RSK-006); câu trả lời sai có thể dẫn tới quyết định kinh doanh sai (RSK-001) | |
| PO phê duyệt intent | | ☐ Phê duyệt ☐ Phê duyệt có điều kiện ☐ Từ chối |

## 9. Ghi chú

- Đây là bản intent cho MVP (theo sơ đồ use case). Thay đổi phạm vi về sau cần cập nhật intent trước khi cập nhật BRD/PRD.
