# Traceability — "Chat với tài liệu" (MVP)

> **Mục đích:** ma trận truy vết hai chiều BRD → PRD/User Story → Use case → Thành phần thiết kế → Cổng phát hành. Ma trận và kiểm tra độ phủ dưới đây được tạo bằng cách đọc trực tiếp BRD, `USER_STORIES.md`, sơ đồ use case và SDD §5.2, không nhập tay.
> **Nguồn:** `docs/02-requirements/BRD.md` (v0.6), `docs/03-analysis/PRD.md` (v0.6), `docs/03-analysis/USER_STORIES.md`, `docs/diagrams/use-case-diagram.drawio`, `docs/design/Blueprint_Design.md` (SDD v0.6)
> **Ghi chú về ID:** dự án không có tài liệu SRS riêng; PRD đóng vai trò đặc tả yêu cầu sản phẩm và `BR-xxx` ↔ `US-xxx` là cặp ID truy vết (không dùng mã FR riêng). ID không đánh số lại sau khi loại mục.

## 1. BRD → User Story → Use case → Thiết kế

| BO | SN | BR | Yêu cầu (rút gọn) | Ưu tiên | AC (BRD) | User story | Use case | Thành phần thiết kế (SDD §5.2) | Cổng |
|---|---|---|---|---|---|---|---|---|---|
| BO-001 | SN-001 | BR-001 | Khi người dùng chọn một file PDF hợp lệ, tổ chức shall cho phép người … | Must | AC-001 | US-001 | UC07 | WEB-2, API-2, DAT-2, DAT-3 | G1 |
| BO-001 | SN-001 | BR-002 | Khi tài liệu được tải lên thành công, tổ chức shall thông báo cho ngườ… | Must | AC-002 | US-002 | UC09 | WRK-1…4, API-2, WEB-2 | G1 |
| BO-001 | SN-001 | BR-003 | cho phép người dùng xem danh sách các tài liệu đã tải lên. | Should | AC-003 | US-004 | UC11 | API-2, WEB-2, DAT-1 | G1 |
| BO-001 | SN-001 | BR-004 | Khi người dùng yêu cầu xóa một tài liệu trong kho dùng chung, tổ chức … | Should | AC-004 | US-005 | UC12 | API-2, WRK-5, DAT-1, DAT-2, WEB-2 | G1 |
| BO-001 | SN-001 | BR-005 | hỗ trợ tải lên file PDF có kích thước tối đa [TBD: OQ-009] MB mỗi file… | Must | AC-005 | US-001 | UC07, UC08 | API-2, API-9, WEB-2 | G1 |
| BO-001 | SN-002 | BR-006 | Khi người dùng nhập một câu hỏi bằng ngôn ngữ tự nhiên, tổ chức shall … | Must | AC-006 | US-006 | UC14, UC21 | WEB-3, API-3, API-4, API-5 | G1 |
| BO-002 | SN-003 | BR-007 | Khi câu trả lời được tạo từ nội dung tài liệu, tổ chức shall cho người… | Must | AC-007 | US-007 | UC15, UC21 | API-3, WEB-3 | G1, G4 |
| BO-002 | SN-003 | BR-008 | Khi câu trả lời dựa trên một vị trí xác định trong tài liệu, tổ chức s… | Should | AC-008 | US-008 | UC16, UC17 | WRK-2, WRK-3, API-3, WEB-3, WEB-4 | G1 |
| BO-002 | SN-004 | BR-009 | Khi câu hỏi cần thông tin từ nhiều hơn một tài liệu, tổ chức shall tổn… | Must | AC-009 | US-009 | UC18 | API-4 (đa dạng hóa), API-3 | G1 |
| BO-002 | SN-003 | BR-010 | Khi tập tài liệu đã tải lên không chứa thông tin để trả lời, tổ chức s… | Must | AC-010 | US-010 | UC19 | API-3, API-4, WEB-3 | G1, G5 |
| BO-002 | SN-003 | BR-011 | đạt tỷ lệ câu trả lời đúng tối thiểu [TBD: OQ-004] % trên bộ câu hỏi k… | Must | AC-011 | — (cổng) | — | PLT-4, API-3, API-4, API-5 | G3 |
| — | SN-006 | BR-016 | lưu trữ tài liệu tải lên tại nơi lưu trữ đáp ứng yêu cầu về vị trí dữ … | Must | AC-016 | US-015 | UC09 | DAT-1, DAT-2, API-5, PLT-1 | G8 |
| BO-001 | SN-001 | BR-018 | Khi việc tải một file lên không thành công, tổ chức shall thông báo ch… | Must | AC-018 | US-003 | UC10 | WRK-2, API-2, WEB-2 | G1 |

Ghi chú: BR-005 phục vụ US-001-AC2 (file vượt giới hạn), UC08 kiểm tra file. BR-011 là điều kiện phát hành G3, không có story riêng. BR-016 chưa gắn BO (OQ-012).

## 2. Use case → BR → User Story

| Use case | Tên | BR | User story |
|---|---|---|---|
| UC07 | Tải PDF lên | BR-001, BR-005 | US-001 |
| UC08 | Kiểm tra file (định dạng, kích thước) | BR-005 | US-001 |
| UC09 | Xử lý & lưu trữ tài liệu, báo sẵn sàng | BR-002, BR-016 | US-002, US-015 |
| UC10 | Báo lỗi tải lên và nêu lý do | BR-018 | US-003 |
| UC11 | Xem danh sách tài liệu & trạng thái | BR-003 | US-004 |
| UC12 | Xóa tài liệu | BR-004 | US-005 |
| UC14 | Đặt câu hỏi bằng ngôn ngữ tự nhiên | BR-006 | US-006 |
| UC15 | Hiển thị nguồn trích dẫn | BR-007 | US-007 |
| UC16 | Hiển thị số trang của nguồn | BR-008 | US-008 |
| UC17 | Mở tài liệu nguồn để đối chiếu | BR-008 | US-008 |
| UC18 | Tổng hợp từ nhiều tài liệu | BR-009 | US-009 |
| UC19 | Báo không tìm thấy thông tin | BR-010 | US-010 |
| UC21 | Truy xuất nội dung & sinh câu trả lời | BR-006, BR-007 | US-006, US-007 |

## 3. User story → BR → Use case → Số AC

| User story | Ưu tiên | BR | Use case | Số tiêu chí chấp nhận |
|---|---|---|---|---|
| US-001 | P0 | BR-001, BR-005 | UC07, UC08 | 3 |
| US-002 | P0 | BR-002 | UC09 | 2 |
| US-003 | P0 | BR-018 | UC10 | 4 |
| US-004 | P1 | BR-003 | UC11 | 1 |
| US-005 | P1 | BR-004 | UC12 | 2 |
| US-006 | P0 | BR-006 | UC14, UC21 | 3 |
| US-007 | P0 | BR-007 | UC15 | 2 |
| US-008 | P1 | BR-008 | UC16, UC17 | 1 |
| US-009 | P0 | BR-009 | UC18 | 2 |
| US-010 | P0 | BR-010 | UC19 | 2 |
| US-015 | P0 | BR-016 | UC09 | 1 |

## 4. Yêu cầu phi chức năng và giao diện → nguồn → thiết kế

| ID | Nội dung | Nguồn | Thiết kế (SDD §5.2) |
|---|---|---|---|
| NFR-PRF-002 | Tài liệu sẵn sàng trong ≤ `[TBD: OQ-P07]` phút | BR-002 | WRK-1…4; QAS-02 |
| NFR-CAP-001 | Kích thước file và số tài liệu tối đa | BR-005 | API-2, API-9 |
| NFR-SCL-001 | Phục vụ đồng thời tối thiểu `[TBD: OQ-001]` người dùng | BO-001 | SS-2, SS-3, API-9; QAS-03 |
| NFR-SCL-002 | Báo "hệ thống bận", giữ nguyên tài liệu đã tải | RSK-P02 | API-9, WEB-3; QAS-03 |
| NFR-SEC-001 | Mã hóa kênh truyền | SN-006, CON-004 | Z1 (TLS), PLT-1; QAS-06 |
| NFR-SEC-002 | Mã hóa dữ liệu lưu trữ | SN-006, CON-004 | DAT-1, DAT-2, PLT-1; QAS-06 |
| IF-02 | Dịch vụ AI bên ngoài | DEP-003 | API-5 |
| IF-03 | Kho lưu trữ tài liệu | BR-016 | DAT-2, API-2, WRK-2, WRK-5 |

## 5. Cổng phát hành → yêu cầu / bằng chứng

| Cổng | Nội dung | Yêu cầu gốc | Bằng chứng |
|---|---|---|---|
| G1 | 100% story P0 đạt AC | US P0 | Báo cáo kiểm thử |
| G3 | Tỷ lệ đúng trên bộ kiểm thử | BR-011, MET-002 | PLT-4; bộ câu hỏi (DEP-002) |
| G4 | 100% câu trả lời có nguồn đúng | BR-007, AC-007 | PLT-4 + lấy mẫu |
| G5 | Câu hỏi ngoài tài liệu nhận "không tìm thấy" | BR-010, AC-010 | PLT-4 |
| G8 | Chính sách vị trí lưu trữ được duyệt | BR-016, AC-016 | Chữ ký CNTT/Pháp lý (OQ-005) |
| G9 | Không có lỗ hổng cao/nghiêm trọng | NFR-SEC-001, 002 | Quét và rà soát bảo mật |
| G11 | Có quy trình xóa tài liệu khi có sự cố | BR-004, RSK-002 | Tài liệu quy trình |
| G12 | Business owner xác nhận kết quả thử | BO-001, BO-002 | Biên bản UAT |
| G13 | NFR mức Must đạt | NFR-CAP-001, NFR-SEC-001, 002 | Báo cáo kiểm thử NFR |

## 6. Báo cáo độ phủ (tính tự động)

| Kiểm tra | Kết quả |
|---|---|
| Số BR trong BRD §7 | 13 |
| BR không có user story (ngoại trừ BR-011 là cổng G3) | 0  |
| BR không có thành phần thiết kế | 0 |
| BR không có hàng BO/SN trong BRD §11 | 0 |
| Số user story | 11 |
| User story không gắn BR | 0  |
| Số use case trong sơ đồ | 13 |
| Use case không gắn BR (theo danh mục trang 2 của sơ đồ) | 0  |
| Tiêu chí chấp nhận BRD (AC-xxx): số lượng / trỏ tới BR không tồn tại | 13 / 0 |

## 7. Việc còn lại

- BR-016 chưa có mục tiêu nghiệp vụ (OQ-012).
- Chưa có cột truy vết xuống test case (thuộc giai đoạn kiểm thử).
- PM/PO và Tech Lead chưa review; chưa baseline (dự án chưa dùng git).
