# User Stories — "Chat với tài liệu" (MVP)

> **Nguồn:** `docs/03-analysis/PRD.md` (v0.6), `docs/02-requirements/BRD.md` (v0.6), `docs/diagrams/use-case-diagram.drawio`
> **Phạm vi:** 11 user story (US-001…US-010, US-015) cho 13 use case của sơ đồ. ID không đánh số lại sau khi loại story (khoảng trống là có chủ ý).
> **Quy ước:** P0 = bắt buộc để phát hành (*Must* trong BRD); P1 = nên có (*Should*). Mỗi story gắn một hoặc nhiều `BR-xxx` (và use case). Dự án không dùng mã FR riêng: `BR-xxx` của BRD và `US-xxx` ở đây là cặp ID dùng cho truy vết (xem `traceability.md`). Tiêu chí chấp nhận có ID dạng `US-xxx-ACn` để không nhầm với `AC-xxx` của BRD. Giá trị `[TBD]` được giữ nguyên, không bịa.
> **Định dạng:** "Là *[vai]*, tôi muốn *[khả năng]*, để *[lợi ích]*" và tiêu chí Given-When-Then.

## 0. Ma trận story

| Story | Ưu tiên | BR | Use case | Số AC |
|---|---|---|---|---|
| US-001 Tải PDF | P0 | BR-001, BR-005 | UC07, UC08 | 3 |
| US-002 Biết khi sẵn sàng | P0 | BR-002 | UC09 | 2 |
| US-003 Biết lý do lỗi tải | P0 | BR-018 | UC10 | 4 |
| US-004 Xem danh sách | P1 | BR-003 | UC11 | 1 |
| US-005 Xóa tài liệu | P1 | BR-004 | UC12 | 2 |
| US-006 Hỏi bằng ngôn ngữ tự nhiên | P0 | BR-006 | UC14, UC21 | 3 |
| US-007 Thấy tài liệu nguồn | P0 | BR-007 | UC15 | 2 |
| US-008 Biết trang chứa thông tin | P1 | BR-008 | UC16, UC17 | 1 |
| US-009 Tổng hợp nhiều tài liệu | P0 | BR-009 | UC18 | 2 |
| US-010 Báo không tìm thấy | P0 | BR-010 | UC19 | 2 |
| US-015 Vị trí lưu trữ | P0 | BR-016 | UC09 | 1 |
| (cổng G3) Ngưỡng chính xác | P0 | BR-011 | — | — |

## 1. E1 — Quản lý tài liệu

**US-001 (P0)** — Là *nhân viên phát triển kinh doanh*, tôi muốn *tải một file PDF lên*, để *đưa tài liệu vào kho tra cứu chung*. *(BR-001, BR-005)*
*Use case: UC07, UC08*
- **US-001-AC1.** Given tôi có một file PDF hợp lệ kích thước ≤ [TBD: OQ-009] MB, When tôi chọn file để tải lên, Then file được nhận và đưa vào kho tài liệu.
- **US-001-AC2.** Given file lớn hơn [TBD: OQ-009] MB, When tôi tải lên, Then file bị từ chối và tôi thấy giới hạn kích thước tối đa.
- **US-001-AC3.** Given file không phải PDF (BRU-003), When tôi tải lên, Then file bị từ chối và tôi được báo chỉ hỗ trợ PDF.

**US-002 (P0)** — Là *nhân viên phát triển kinh doanh*, tôi muốn *biết khi nào tài liệu đã sẵn sàng để hỏi*, để *không đặt câu hỏi khi tài liệu chưa được xử lý xong*. *(BR-002)*
*Use case: UC09*
- **US-002-AC1.** Given tôi vừa tải thành công một PDF, When tài liệu sẵn sàng tra cứu, Then tôi thấy thông báo "đã sẵn sàng" gắn với tên tài liệu đó.
- **US-002-AC2.** Given tài liệu chưa sẵn sàng, When tôi đặt câu hỏi, Then tôi thấy trạng thái "đang xử lý" và câu trả lời không dùng nội dung tài liệu đó.

**US-003 (P0)** — Là *nhân viên phát triển kinh doanh*, tôi muốn *biết lý do khi tải file thất bại*, để *tự xử lý được mà không mất thời gian*. *(BR-018)*
*Use case: UC10*
- **US-003-AC1.** Given file PDF bị hỏng, When tôi tải lên, Then tải thất bại và tôi thấy thông báo nêu lý do "file bị hỏng" cùng hướng xử lý (tải lại file khác).
- **US-003-AC2.** Given file PDF có mật khẩu, When tôi tải lên, Then tải thất bại và tôi thấy thông báo nêu lý do "file có mật khẩu" cùng hướng xử lý (bỏ mật khẩu rồi tải lại).
- **US-003-AC3.** Given file PDF không có văn bản trích xuất được (dạng ảnh quét), When tôi tải lên, Then tài liệu không được đánh dấu "sẵn sàng" và tôi thấy thông báo nêu lý do này (ASM-001, RSK-005).
- **US-003-AC4.** Given mất kết nối trong lúc tải, When kết nối được khôi phục, Then tôi thấy trạng thái thất bại và có thể thử lại, không có tài liệu "nửa vời" trong danh sách.

**US-004 (P1)** — Là *nhân viên phát triển kinh doanh*, tôi muốn *xem danh sách tài liệu đã tải*, để *biết phạm vi tra cứu hiện tại*. *(BR-003)*
*Use case: UC11*
- **US-004-AC1.** Given tôi đã tải ít nhất một tài liệu, When tôi mở danh sách tài liệu, Then tôi thấy đầy đủ các tài liệu của tôi kèm tên và trạng thái (sẵn sàng / đang xử lý / lỗi).

**US-005 (P1)** — Là *nhân viên phát triển kinh doanh*, tôi muốn *xóa tài liệu đã tải*, để *loại nội dung lỗi thời hoặc không cần khỏi kết quả tra cứu*. *(BR-004)*
*Use case: UC12*
- **US-005-AC1.** Given một tài liệu do tôi tải lên, When tôi yêu cầu xóa và xác nhận, Then tài liệu biến mất khỏi danh sách của tôi.
- **US-005-AC2.** Given tài liệu đã bị xóa, When tôi đặt câu hỏi liên quan nội dung tài liệu đó, Then câu trả lời không chứa nội dung hay tên của tài liệu đó.

## 2. E2 — Hỏi đáp trên tài liệu

**US-006 (P0)** — Là *nhân viên phát triển kinh doanh*, tôi muốn *đặt câu hỏi bằng ngôn ngữ tự nhiên*, để *nhận câu trả lời dựa trên nội dung tài liệu của tôi mà không phải đọc từng file*. *(BR-006)*
*Use case: UC14, UC21*
- **US-006-AC1.** Given tôi có ít nhất một tài liệu ở trạng thái sẵn sàng, When tôi gửi một câu hỏi thuộc bộ câu hỏi kiểm thử, Then tôi nhận được câu trả lời mà nội dung khớp với tài liệu theo đánh giá của người chấm (ngưỡng tổng thể tại G3).
- **US-006-AC2.** Given tôi chưa có tài liệu nào, When tôi mở khung hỏi đáp, Then tôi thấy hướng dẫn tải tài liệu trước (trạng thái trống) và không thể gửi câu hỏi.
- **US-006-AC3.** Given câu hỏi nằm trong ngôn ngữ [TBD: OQ-011], When tôi gửi, Then câu trả lời bằng cùng ngôn ngữ với câu hỏi.

**US-007 (P0)** — Là *trưởng nhóm kinh doanh*, tôi muốn *thấy câu trả lời dựa vào tài liệu nào*, để *kiểm chứng trước khi dùng cho quyết định*. *(BR-007)*
*Use case: UC15*
- **US-007-AC1.** Given một câu trả lời có nội dung lấy từ tài liệu, When câu trả lời hiển thị, Then ngay bên dưới có danh sách tài liệu nguồn đúng với tài liệu mà thông tin được lấy.
- **US-007-AC2.** Given câu trả lời lấy từ N tài liệu, When hiển thị, Then liệt kê đủ N tài liệu đó, không thừa tài liệu không liên quan.

**US-008 (P1)** — Là *trưởng nhóm kinh doanh*, tôi muốn *biết trang chứa thông tin*, để *đối chiếu nhanh mà không đọc lại cả tài liệu*. *(BR-008)*
*Use case: UC16, UC17*
- **US-008-AC1.** Given câu trả lời dựa trên một vị trí xác định trong tài liệu, When câu trả lời hiển thị, Then số trang hiển thị khớp trang chứa nội dung đó trong mẫu kiểm tra.

**US-009 (P0)** — Là *nhân viên phát triển kinh doanh*, tôi muốn *một câu trả lời tổng hợp từ nhiều tài liệu*, để *không phải tự ghép thông tin từ nhiều file*. *(BR-009)*
*Use case: UC18*
- **US-009-AC1.** Given tôi có ≥ 2 tài liệu cùng chứa thông tin liên quan đến câu hỏi, When tôi gửi câu hỏi, Then câu trả lời có thông tin từ cả các tài liệu đó và liệt kê từng nguồn.
- **US-009-AC2.** Given hai tài liệu có thông tin mâu thuẫn nhau, When tôi hỏi, Then câu trả lời nêu rõ có khác biệt và chỉ ra từng nguồn, không tự chọn một bên.

**US-010 (P0)** — Là *nhân viên phát triển kinh doanh*, tôi muốn *được báo rõ khi tài liệu không có thông tin*, để *không bị dẫn dắt bởi câu trả lời không có căn cứ*. *(BR-010, BRU-001)*
*Use case: UC19*
- **US-010-AC1.** Given tập tài liệu của tôi không chứa thông tin cho câu hỏi, When tôi gửi câu hỏi, Then tôi nhận thông báo "không tìm thấy thông tin trong các tài liệu đã tải" và không nhận nội dung bịa.
- **US-010-AC2.** Given câu hỏi chỉ trả lời được một phần, When tôi gửi, Then câu trả lời nêu phần có căn cứ và nói rõ phần nào không tìm thấy.

## 3. E3 — Bảo mật, dữ liệu

**US-015 (P0)** — Là *đại diện CNTT/bảo mật (UC-P4)*, tôi muốn *tài liệu được lưu tại nơi đáp ứng yêu cầu vị trí dữ liệu*, để *tuân thủ chính sách*. *(BR-016, [TBD: OQ-005])*
*Use case: UC09 (IF-03)*
- **US-015-AC1.** Given chính sách vị trí dữ liệu đã được phê duyệt, When rà soát cấu hình lưu trữ, Then vị trí lưu trữ khớp chính sách.

## 4. Ghi chú phạm vi

- **Tính chính xác câu trả lời (BR-011, Must)** không phải một story của người dùng mà là điều kiện phát hành (PRD §5.1). Chưa có ngưỡng cho tới khi OQ-004 được trả lời.
- Một số story P0 phụ thuộc quyết định chưa có (US-001-AC2, US-015). Chúng vẫn là P0 vì BR tương ứng là *Must*, nhưng không thể kiểm thử cho tới khi OQ liên quan đóng.
