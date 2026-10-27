# Stakeholders — "Chat với tài liệu" (MVP)

> **Nguồn:** BRD §6, §6.1; PRD §2.1; SDD §2.1; SADD §2.3
> **Trạng thái:** Draft. Tên người cụ thể chưa có (`[TBD: OQ-007]`); bảng này chỉ ghi vai trò.
> **Ngôn ngữ:** Tiếng Việt

## Bên liên quan

| ID | Bên liên quan | Vai trò | Mối quan tâm chính | Ảnh hưởng | Người dùng trực tiếp? | Nguồn |
|---|---|---|---|---|---|---|
| STK-001 | Đội phát triển kinh doanh | Người dùng chính (UC-P1) | Tìm thông tin nhanh, đúng, có nguồn; tải tài liệu không lỗi | Cao | Có | SRC-001 |
| STK-002 | Quản lý (người yêu cầu MVP) | Sponsor | Chứng minh giá trị MVP bằng thử nghiệm có chủ đích | Cao | Không | SRC-001, `[Unverified]` |
| STK-003 | CNTT / bảo mật / pháp lý | Phê duyệt chính sách dữ liệu (UC-P4) | Nơi lưu trữ, mã hóa, rò rỉ dữ liệu, chấp nhận CON-005 | Trung bình | Không | `[Unverified]` — OQ-005 |
| STK-004 | Chủ sở hữu / người phát hành tài liệu | Sở hữu nội dung PDF | Tài liệu không bị lộ hoặc dùng sai | Trung bình | Không | `[Unverified]` — OQ-005 |
| STK-005 | Người dùng hoài nghi | Có thể cản trở áp dụng | Lo AI trả lời sai; thay đổi thói quen | Trung bình | Có | `[Unverified]` — OQ-008 |
| STK-006 | Nhà cung cấp dịch vụ AI / hạ tầng (nếu có) | Bên ngoài | Điều khoản sử dụng, bảo mật dữ liệu | Thấp | Không | `[Unverified]` — OQ-005 |

## Người dùng (user classes)

| ID | Nhóm | Ngữ cảnh sử dụng | Quy mô / tần suất | Mức quen AI | Ghi chú |
|---|---|---|---|---|---|
| UC-P1 | Nhân viên phát triển kinh doanh | Cần một thông tin cụ thể nhanh, thường nằm trong nhiều PDF | `[TBD: OQ-001]` | `[TBD: OQ-008]` | Actor người trong sơ đồ use case |
| UC-P2 | Trưởng nhóm / quản lý kinh doanh | Cần tổng hợp xuyên nhiều tài liệu và kiểm chứng nguồn | `[TBD: OQ-001]` | `[TBD: OQ-008]` | `[Unverified]`; actor người trong sơ đồ |

## Actor trong sơ đồ use case

| Actor | Loại | Use case liên quan | Ghi chú |
|---|---|---|---|
| Người dùng kinh doanh | Người (actor chính) | UC07, UC11, UC12, UC14 (và các UC con được include/extend) | Ánh xạ UC-P1, UC-P2 |
| Kho lưu trữ tài liệu (IF-03) | Hệ thống ngoài («system») | UC09 | Có thể do nền tảng cung cấp; chờ OQ-005 |
| Dịch vụ AI bên ngoài (IF-02, nếu có) | Hệ thống ngoài («system») | UC21 | Có thể tự lưu trữ; chờ OQ-005, DEP-003. Ánh xạ STK-006 |

## Bên liên quan không phải actor trong sơ đồ use case

| ID | Vai | Lý do không phải actor |
|---|---|---|
| UC-P4 | CNTT / bảo mật | Tham gia phê duyệt chính sách, không có màn hình hay use case |

## Vai kỹ thuật (đội thực hiện)

| Vai | Mối quan tâm chính | Nguồn |
|---|---|---|
| Lead Architect / Developer | Dễ thay đổi, kiểm thử được, dễ thay nhà cung cấp AI | SADD §2.3 |
| QA | Kiểm thử chất lượng AI lặp lại; bộ câu hỏi chuẩn (DEP-002) | SADD §2.3 |
| DevOps / SRE | Triển khai, giám sát, khôi phục | SADD §2.3 |
| Designer | Trạng thái, khả năng tiếp cận, thông báo dữ liệu | UIUX §1 |
| AI / dữ liệu | Chất lượng truy xuất và sinh câu trả lời; tham số RAG | SADD §4.6 |

## Người phê duyệt (để điền ở bước 4)

| Vai | Tên | Quyết định |
|---|---|---|
| Sponsor điều hành | `[TBD: OQ-007]` | |
| Business owner | `[TBD: OQ-007]` | |
| Product owner | `[TBD: OQ-007]` | |
| Tuân thủ / pháp lý | `[TBD: OQ-007]` | |
