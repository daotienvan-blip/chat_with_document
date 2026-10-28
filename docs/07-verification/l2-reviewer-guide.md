# Hướng dẫn cho người duyệt L2 — "Chat với tài liệu"

> Dành cho người được chỉ định duyệt L2. Đọc tệp này trước, rồi **đọc diff** — không dựa vào `review-record.md` §4–§6 (đó là ý kiến của agent, đã biết là không độc lập).
> Kết quả ghi vào `review-record.md` §8.

## 1. Ai được duyệt

| Điều kiện | Lý do |
|---|---|
| **Không phải** Dao Tien Van (tác giả mọi commit trên `main`) và **không phải** agent (người viết mã) | Quy tắc "1 approver ≠ author" |
| Đọc được Python + TypeScript, biết SQL/PostgreSQL ở mức đọc truy vấn | Diff gồm server FastAPI, web React, SQL |
| Có quyền ghi trên repo `daotienvan-blip/chat_with_document` để approve PR | Approval phải nằm trên PR, không chỉ trong tài liệu |
| Không chịu áp lực tiến độ trực tiếp từ dự án (khuyến nghị) | Giảm thiên lệch "cho qua" |

Người chỉ định: chủ dự án / người chịu trách nhiệm `[TBD: OQ-007]`. Ghi tên vào bảng §8 trước khi bắt đầu.

## 2. Duyệt cái gì, theo thứ tự

| Thứ tự | Đối tượng | Kích thước | Cách lấy diff |
|---|---|---|---|
| 1 | **RO-1** — PR giai đoạn 7 (CI L0 + sửa kiểu) | ~210 dòng | Trên PR nhánh `verify/phase-7-ci` (khi đã đẩy lên); trước đó: `git diff` trong thư mục dự án |
| 2 | **RO-2** — hồi tố, lát L2-1 → L2-12 | ≤ ~400 dòng/lát | `git diff 24c2c46 ec18ff6 -- app/<đường dẫn lát>` (bảng lát: `review-record.md` §7) |
| 3 | Các PR sửa F-01, F-02, F-03 (khi có) | mỗi PR một lỗi | Trên PR |

Mỗi phiên tối đa ~400 dòng, ≤ 60 phút. Lát lớn hơn ⇒ tách.

## 3. Cách chấm rubric (0 / 1 / 2)

| Tiêu chí | 2 = đạt | 1 = đạt một phần | 0 = không đạt |
|---|---|---|---|
| Đúng AC | Diff làm đúng AC/task được trỏ tới, không thêm ngoài phạm vi | Đúng phần chính, thiếu ca biên hoặc có sai lệch nhỏ | Sai hoặc không làm được AC |
| Test | Có test cho hành vi mới/sửa, kể cả ca lỗi; CI xanh | Có test nhưng thiếu ca lỗi/biên | Không test hoặc CI đỏ |
| Thiết kế | Khớp SAD/ports & adapters; không phá hợp đồng import-linter | Chạy được nhưng đặt sai tầng / trùng lặp | Phá kiến trúc |
| An toàn | Đầu vào được kiểm, không lộ bí mật/nội dung, quyền tối thiểu | Có lỗ hổng nhỏ, có giới hạn | Lỗ hổng khai thác được |
| Hiệu năng | Không có vòng lặp/tài nguyên không giới hạn | Có rủi ro được ghi nhận | Có lỗi tài nguyên rõ ràng |
| Dễ đọc | Tên rõ, hàm ngắn, chú thích nêu lý do | Đọc được nhưng cần sửa | Khó hiểu |
| Truy vết | Trỏ được về story/AC/task; test có marker `req` | Trỏ được một phần | Không truy vết được |

**Merge khi:** tổng ≥ 10/14 **và** không còn phát hiện Major mở trong chính diff đó. Không có tiêu chí nào được 0.

## 4. Bắt buộc kiểm trước khi approve RO-1

- [ ] Lượt CI đầu tiên trên GitHub: 4 job (`server`, `web`, `secrets`, `images`) xanh, mỗi job < 10 phút.
- [ ] Job `server` thật sự chạy 29 test `integration` (xem log pytest, không bị skip).
- [ ] `fail_under = 70` (`app/server/pyproject.toml`) và `thresholds` (`app/web/vite.config.ts`) không bị hạ.
- [ ] `.gitleaksignore` chỉ có dấu vân tay đã giải thích (khóa sessionStorage `cwd.conversation.v1`).
- [ ] 4 sửa kiểu (`retrieval/service.py`, `validate_upload.py`, `runner.py`, `pymupdf_extractor.py`) không đổi hành vi.

## 5. Ghi kết quả

1. Ghi phát hiện của bạn thành comment trên dòng trong PR (tệp:dòng, mức Major/Minor/Góp ý).
2. Điền một dòng vào `review-record.md` §8: tên, 7 điểm, tổng, quyết định, ngày.
3. Approve hoặc Request changes **trên GitHub**. Agent không approve, merge hay deploy.
4. Phát hiện mới mà agent bỏ sót: thêm vào `review-record.md` §4 với mã F-15 trở đi, ghi "nguồn: L2".
