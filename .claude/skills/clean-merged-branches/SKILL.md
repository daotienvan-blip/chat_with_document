---
name: clean-merged-branches
description: Dọn nhánh git đã merge vào main (cục bộ, tùy chọn cả trên origin) cho repo "Chat với tài liệu". Dùng khi người dùng nói "xóa nhánh đã merge", "dọn branch", hoặc sau khi PR được merge.
---

# Dọn nhánh đã merge

Hook tự động (`.claude/settings.json`) đã xóa nhánh **cục bộ** đã merge khi bắt đầu phiên và sau các lệnh `git pull/merge/checkout/switch/fetch`, `gh pr merge`. Skill này dùng khi cần dọn thủ công hoặc xóa cả nhánh trên origin.

Script: `.claude/hooks/cleanup-merged-branches.py` (chỉ dùng thư viện chuẩn, chạy được với python3 3.9 của macOS).

## Cách dùng

Luôn xem trước:

```bash
python3 .claude/hooks/cleanup-merged-branches.py --fetch --dry-run
```

Rồi xóa nhánh cục bộ:

```bash
python3 .claude/hooks/cleanup-merged-branches.py --fetch
```

Xóa cả nhánh trên origin (thao tác trên remote — **chỉ làm khi người dùng yêu cầu rõ**, và cho họ xem kết quả `--dry-run --remote` trước):

```bash
python3 .claude/hooks/cleanup-merged-branches.py --fetch --remote
```

## Cách script quyết định

- "Đã merge" = đầu nhánh là cha thứ hai của một merge commit trên đường first-parent của `origin/main` (repo này merge PR bằng merge commit). Nhánh mới tạo, chưa có commit, **không** bị xóa nhầm.
- Không bao giờ xóa `main`, `master`, `develop`, nhánh đang checkout hoặc đang mở ở worktree khác.
- Nhánh có upstream đã bị xóa (`[gone]`) nhưng không chứng minh được đã merge (ví dụ squash merge) chỉ được liệt kê. Hỏi người dùng rồi mới xóa tay bằng `git branch -D <tên>`.
- Mỗi nhánh đã xóa được in kèm SHA để khôi phục: `git branch <tên> <sha>`.

## Lưu ý

GitHub có thể tự xóa nhánh sau merge (Settings → General → "Automatically delete head branches"); bật tùy chọn đó là cách gọn nhất cho phía origin. Agent không đổi cài đặt repo.
