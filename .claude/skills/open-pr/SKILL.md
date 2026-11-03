---
name: open-pr
description: Tạo nhánh, commit và mở PR cho repo "Chat với tài liệu" đúng quy trình dự án (PR ≤ 400 dòng, commit tiếng Việt, CI xanh, agent không approve/merge). Dùng khi người dùng nhờ commit, push hoặc mở PR.
---

# Tạo nhánh, commit, mở PR

## Quy tắc cứng của dự án

- Agent **được** tạo nhánh, commit, mở PR khi người dùng yêu cầu. Agent **không** approve, merge, deploy hay đổi production. Approver phải khác tác giả.
- Không push thẳng lên `main`. Mỗi thay đổi một nhánh + một PR.
- Commit message, mô tả PR, chú thích mã và chuỗi hiển thị bằng **tiếng Việt**.
- Không commit bí mật. `.env`, token, `CWD_GITHUB_PAT` không bao giờ vào git; CI quét gitleaks toàn bộ lịch sử.

## Quy trình

1. Đảm bảo đang ở nhánh cập nhật từ `main`, tạo nhánh có tiền tố theo loại việc: `feat/…`, `fix/…`, `docs/…`, `verify/…`.
2. Giữ PR nhỏ. Đo bằng `git diff --shortstat origin/main...HEAD -- . ':!app/web/package-lock.json' ':!app/web/src/api-client/generated.ts'`. Nếu vượt **400 dòng viết tay**, tách thành nhiều PR.
3. Chạy `make ci` từ `app/` (hoặc tối thiểu `make check`, nói rõ mức đã chạy). Không mở PR khi đỏ.
4. Sửa lỗi thì cập nhật tài liệu cổng/hồ sơ tương ứng **trong cùng PR**: `docs/07-verification/review-record.md`, `docs/05-implement/release-gates.md`; sự cố thật vào `docs/10-operations/incidents/`.
5. Commit: một dòng tóm tắt tiếng Việt nêu việc đã làm và mã yêu cầu nếu có, ví dụ `Giao diện: chặn tệp không phải PDF trước khi tải lên (US-001-AC3)`.
6. Mô tả PR theo mẫu `docs/07-verification/pr-description.md`: Tóm tắt · Kết quả kiểm tra (dán kết quả thật) · Người duyệt cần kiểm · Ngoài phạm vi · Truy vết.
7. Sau khi mở PR, dừng lại báo link cho người dùng. Không tự merge.

## Dọn nhánh sau merge

Hook `.claude/hooks/cleanup-merged-branches.py` tự xóa nhánh cục bộ đã merge vào `main`. Muốn dọn tay hoặc xóa cả nhánh trên origin, dùng skill `clean-merged-branches`.
