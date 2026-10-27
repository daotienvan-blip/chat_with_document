# S8-08 — Kiểm thử E2E (Playwright) và kiểm tra tiếp cận tự động

| | |
|---|---|
| **Lát cắt** | S8 — Củng cố, vận hành và cổng phát hành (mốc M4) |
| **Cỡ** | M (3–6 vòng lặp) |
| **Đường** | Web |
| **Phụ thuộc** | [S6-03](S6-03-web-hop-thoai-xac-nhan-xoa-nguon-da-xoa-va.md), [S4-03](S4-03-web-nguon-dang-chip-va-mo-tai-lieu-nguon-o.md), [S7-03](S7-03-web-xu-ly-loi-hoi-dap-theo-scr-05-thu-lai.md), [S2-05](S2-05-worker-entrypoint-vong-quet-tat-em-va-kiem.md), [S5-02](S5-02-web-hien-thi-tra-loi-mot-phan-va-nhieu-nguon.md) |
| **Truy vết** | G1, G12, QAS-01, Accessibility |
| **Bị chặn bởi** | Không (có giá trị mặc định/cấu hình để làm tiếp) |
| **Trạng thái** | ⛔ Chưa làm / bị chặn — Playwright + axe chưa làm; thay tạm bằng `smoke.py` + test thành phần |

## Mục tiêu

Các hành trình chính chạy trên toàn hệ thống thật (compose, `FakeLlm`) và không có vi phạm tiếp cận tự động.

## Đọc trước

- PRD G1, G12
- Blueprint §2.4
- html_design/*
- `docs/05-implement/PLAN.md` §2 (quy trình, định nghĩa hoàn thành) và §3 (quyết định kỹ thuật cố định)

## Phạm vi (tệp được tạo/sửa)

- `e2e/` (Playwright), `make e2e`

## Các bước

1. Hành trình: trống ⇒ tải PDF ⇒ đang xử lý ⇒ sẵn sàng ⇒ hỏi (có căn cứ + nguồn) ⇒ bấm nguồn (URL `/file#page=N`, trả PDF) ⇒ hỏi ngoài tài liệu (`not_found`) ⇒ xóa có xác nhận ⇒ nguồn “(đã xóa)”; tải PDF có mật khẩu ⇒ thấy lý do lỗi.
2. Kịch bản lỗi: dừng `FakeLlm`/mô phỏng AI lỗi ⇒ thông báo + giữ câu hỏi ⇒ khôi phục ⇒ Gửi lại thành công.
3. Chạy axe-core trên từng trạng thái chính; chỉ dùng bàn phím hoàn thành hành trình hỏi đáp và xóa.
4. Đếm số thao tác tới câu trả lời đầu tiên (tài liệu có sẵn ≤ 3; tài liệu mới ≤ 5 — bằng chứng sơ bộ cho G12, không thay thế UAT).

## Tiêu chí hoàn thành

- [ ] `make e2e` xanh trên compose; báo cáo kèm ảnh chụp các trạng thái chính.
- [ ] 0 vi phạm axe mức nghiêm trọng/cao; phần còn lại được liệt kê.
- [ ] Số thao tác đo được ghi trong báo cáo.
- [ ] `make check` xanh (và `make test-int` nếu task có kiểm thử tích hợp); mô tả PR nêu lệnh đã chạy và kết quả thật, kể cả phần **chưa** kiểm tra được

## Ngoài phạm vi

- UAT với người dùng thật (G12) — việc của business owner.
