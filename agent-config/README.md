# agent-config

Cấu hình Claude Code dùng ở thư mục làm việc `SDLC/` (thư mục cha của repo này). Chép nội dung vào gốc `SDLC/`:

| Tệp | Chép thành | Ghi chú |
|---|---|---|
| `CLAUDE.md` | `SDLC/CLAUDE.md` | Nguyên tắc làm việc chung cho agent (CLAUDE.md của repo nằm ở gốc repo, khác tệp này) |
| `.claude/settings.example.json` | `SDLC/.claude/settings.local.json` | Chặn công cụ ghi/merge của GitHub MCP và công cụ xóa của Atlassian; đăng ký hook |
| `.claude/hooks/pdf-only-upload.py` | `SDLC/.claude/hooks/pdf-only-upload.py` | Hook PreToolUse: chặn `curl` tải tệp không phải PDF lên `/api/v1/documents` |
| `.mcp.json.example` | `SDLC/.mcp.json` | Điền token qua biến môi trường `CWD_GITHUB_PAT`; Atlassian đăng nhập OAuth qua `/mcp` |

`.mcp.json` thật **không** được commit vì có thể chứa token. Repo này công khai.
