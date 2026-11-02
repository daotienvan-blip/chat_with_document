#!/usr/bin/env python3
"""Hook PreToolUse (Bash): chặn AI tải tệp không phải PDF lên endpoint tài liệu của ứng dụng.

Chỉ xét lệnh `curl` gọi `/api/v1/documents` (-F/--form, -T/--upload-file, --data-binary). Tệp được coi là PDF khi:
đuôi `.pdf`, `type=` (nếu có) là application/pdf, và 1.024 byte đầu có `%PDF-` (đặc tả PDF cho phép tiêu đề ở đó).
Chắc chắn không phải PDF -> deny. Không xác minh được (biến shell, stdin, lệnh không tách được) -> ask.
Không phải lệnh tải lên -> không in gì, để luồng cấp quyền thường chạy tiếp.
"""
from __future__ import annotations  # python3 mặc định trên macOS là 3.9; hook crash thì lệnh vẫn chạy (không chặn)

import json
import os
import re
import shlex
import sys

MESSAGE = "Please upload pdf file only"
ENDPOINT = "/api/v1/documents"
UNRESOLVED = re.compile(r"[$`*?\[{]")


def decide(decision: str, detail: str) -> None:
    reason = f"{MESSAGE} ({detail})"
    print(json.dumps({
        "systemMessage": f"{MESSAGE}: {detail}",
        "hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision,
                               "permissionDecisionReason": reason},
    }, ensure_ascii=False))
    sys.exit(0)


def upload_refs(tokens: list[str]) -> list[tuple[str, str | None]]:
    """(đường dẫn, type= nếu có) của mọi tệp mà các cờ curl sẽ gửi đi."""
    refs: list[tuple[str, str | None]] = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        val = None
        if t in ("-F", "--form", "-T", "--upload-file", "--data-binary") and i + 1 < len(tokens):
            val, i = tokens[i + 1], i + 1
        elif t.startswith("--form=") or t.startswith("--upload-file=") or t.startswith("--data-binary="):
            val = t.split("=", 1)[1]
        elif t.startswith("-F") and len(t) > 2:
            val = t[2:]
        elif t.startswith("-T") and len(t) > 2:
            val = t[2:]
        i += 1
        if val is None:
            continue
        flag_is_upload = t.startswith(("-T", "--upload-file"))
        if flag_is_upload:
            path, rest = (val.split(";", 1) + [""])[:2]
        else:
            m = re.match(r"^[^=]*=([@<])(.*)$", val, re.S) if t.startswith(("-F", "--form")) else re.match(r"^(@)(.*)$", val, re.S)
            if not m:
                continue  # trường chữ, không phải tệp
            path, rest = (m.group(2).split(";", 1) + [""])[:2]
        mt = re.search(r"(?:^|;)type=([^;]+)", rest)
        refs.append((path.strip("\"'"), mt.group(1).strip() if mt else None))
    return refs


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Bash":
        return
    cmd = (data.get("tool_input") or {}).get("command", "")
    if ENDPOINT not in cmd or not re.search(r"\bcurl\b", cmd):
        return
    try:
        lex = shlex.shlex(cmd, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        tokens = list(lex)
    except ValueError:
        decide("ask", "không phân tích được lệnh curl nên chưa xác minh được tệp gửi lên")
    cwd = data.get("cwd") or os.getcwd()
    for path, mime in upload_refs(tokens):
        name = os.path.basename(path) or path
        if path in ("-", ""):
            decide("ask", "tệp gửi từ stdin, chưa xác minh được")
        if UNRESOLVED.search(path):
            decide("ask", f"đường dẫn {path} chứa biến hoặc ký tự đại diện, chưa xác minh được; hãy dùng đường dẫn cụ thể")
        if not path.lower().endswith(".pdf"):
            decide("deny", f"{name} không có đuôi .pdf")
        if mime and mime.lower() != "application/pdf":
            decide("deny", f"{name} khai báo loại nội dung {mime}")
        full = os.path.join(cwd, os.path.expanduser(path))
        if os.path.isfile(full):
            with open(full, "rb") as f:
                if b"%PDF-" not in f.read(1024):
                    decide("deny", f"{name} có đuôi .pdf nhưng nội dung không phải PDF")


if __name__ == "__main__":
    main()
