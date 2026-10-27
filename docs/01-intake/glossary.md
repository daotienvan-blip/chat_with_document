# Glossary — "Chat với tài liệu" (MVP)

> **Nguồn:** BRD §13, PRD §1–§5, SADD Phụ lục A. Thuật ngữ mới được thêm khi xuất hiện trong tài liệu khác.
> **Ngôn ngữ:** Tiếng Việt; thuật ngữ kỹ thuật giữ tiếng Anh khi không có tên Việt thống nhất.

## Thuật ngữ nghiệp vụ

| Thuật ngữ | Định nghĩa | Ghi chú |
|---|---|---|
| BRD | Business Requirements Document — tài liệu yêu cầu nghiệp vụ | IEEE 29148-2018 |
| PRD | Product Requirements Document — tài liệu yêu cầu sản phẩm | IEEE 29148-2018 |
| MVP | Minimum Viable Product — sản phẩm khả thi tối thiểu để kiểm chứng giá trị | |
| Chat với tài liệu | Người dùng đặt câu hỏi bằng ngôn ngữ tự nhiên và nhận câu trả lời dựa trên nội dung tài liệu đã tải lên | |
| Tài liệu nguồn | Tài liệu (và trang) mà câu trả lời dựa vào | |
| Kho tài liệu dùng chung | Toàn bộ PDF đã tải lên; mọi người dùng đều truy vấn được (không đăng nhập) | — |
| Câu trả lời đúng | Câu trả lời khớp nội dung tài liệu theo người xác nhận bộ kiểm thử | Định nghĩa chính thức tại OQ-004 |
| Business owner | Người chịu trách nhiệm về kết quả nghiệp vụ của sáng kiến | |
| Cuộc trao đổi | Chuỗi câu hỏi và trả lời trong trình duyệt; máy chủ không lưu | Xem SADD §2.2 |

## Loại phản hồi

| Thuật ngữ | Định nghĩa |
|---|---|
| `answered` (đủ căn cứ) | Câu trả lời có trích dẫn hợp lệ từ tài liệu |
| `partial` (một phần) | Có căn cứ cho một phần câu hỏi; phần còn lại được nêu rõ là không tìm thấy |
| `not_found` (không tìm thấy) | Tài liệu không có thông tin; hệ thống không bịa câu trả lời |

## Thuật ngữ kỹ thuật

| Thuật ngữ | Định nghĩa | Ghi chú |
|---|---|---|
| RAG | Retrieval-Augmented Generation: truy xuất đoạn liên quan rồi mới cho LLM sinh câu trả lời | |
| Chunk (đoạn) | Đơn vị văn bản được lập chỉ mục, có biên trang | |
| Embedding / vector | Biểu diễn số của đoạn văn để tìm kiếm theo ngữ nghĩa | |
| Full-text search (FTS) | Tìm kiếm từ khóa trên văn bản (PostgreSQL `tsvector`) | Kết hợp với vector (truy xuất lai) |
| Grounding | Mức câu trả lời bám vào tài liệu; nguồn hiển thị lấy từ siêu dữ liệu đoạn, không từ văn bản LLM | |
| Trích dẫn | Mã đoạn mà LLM dùng để trả lời; hệ thống kiểm tra mã thuộc tập đã cung cấp | |
| `LlmPort` | Cổng giao tiếp duy nhất tới dịch vụ AI (LLM + embedding) | Ports & Adapters |
| Adapter | Thành phần cài đặt một cổng cho một nhà cung cấp cụ thể | |
| Job | Việc nền (xử lý tài liệu, xóa vật lý), lưu trong bảng `jobs` | Hàng đợi trong CSDL |
| Soft delete | Đánh dấu `deleted_at`; tài liệu bị loại khỏi tra cứu ngay, xóa vật lý sau | |
| Load Guard | Thành phần giới hạn tốc độ và số yêu cầu đồng thời; trả "hệ thống bận" khi vượt | |
| Idempotent | Thực hiện lại không tạo kết quả trùng lặp | Áp dụng cho job và ghi chunk |

## Thuật ngữ sơ đồ use case (UML 2.0)

| Thuật ngữ | Định nghĩa | Trong sơ đồ |
|---|---|---|
| Actor | Đối tượng ngoài hệ thống tương tác với use case | Người dùng kinh doanh (người); IF-02, IF-03 (hệ thống) |
| Actor người | Actor là con người, vẽ hình người | Người dùng kinh doanh |
| Actor hệ thống («system») | Hệ thống bên ngoài tương tác với use case, vẽ hộp có nhãn «system» | Kho lưu trữ tài liệu; Dịch vụ AI bên ngoài |
| Association | Đường nối actor với use case | Người dùng → UC07, UC11, UC12, UC14 |
| «include» | Use case gốc luôn gọi use case con (bắt buộc) | UC07 → UC08, UC09; UC14 → UC15, UC21 |
| «extend» | Use case mở rộng chỉ xảy ra trong điều kiện nhất định (tùy chọn) | UC10 → UC07; UC16, UC17 → UC15; UC18, UC19 → UC14 |
| Generalization | Quan hệ kế thừa giữa các actor hoặc use case | Không có trong sơ đồ |
| Epic | Nhóm nghiệp vụ trong PRD, dùng để gom use case | Nhóm B = Epic E1, Nhóm C = Epic E2 |

## Mã nhận dạng trong tài liệu

| Tiền tố | Ý nghĩa | Ví dụ |
|---|---|---|
| BO | Mục tiêu nghiệp vụ | BO-001 |
| MET | Chỉ số đo lường | MET-001 |
| STK / SN | Bên liên quan / nhu cầu | STK-001, SN-001 |
| UC-P | Nhóm người dùng (persona) | UC-P1 |
| BR / BRU / CON / ASM / DEP / RSK | Yêu cầu / quy tắc / ràng buộc / giả định / phụ thuộc / rủi ro (BRD) | BR-006, CON-005 |
| US / AC / EC | User story / tiêu chí chấp nhận / trường hợp biên (PRD) | US-006, EC-10 |
| UC | Use case trong sơ đồ use case (13 UC: UC07–UC12, UC14–UC19, UC21) | UC14 |
| IF | Giao diện / hệ thống bên ngoài | IF-02, IF-03 |
| SS / API / WRK / DAT / PLT / WEB | Thành phần kiến trúc (SDD) | API-3, WRK-2 |
| ADR | Quyết định kiến trúc | ADR-05 |
| OQ | Câu hỏi mở | OQ-005 |
| `[TBD: OQ-xxx]` | Giá trị chờ quyết định | |
| `[Đề xuất]` | Giá trị do tác giả đề xuất, chưa xác nhận | |
| `[Unverified]` | Chưa có nguồn | |
