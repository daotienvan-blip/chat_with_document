#!/usr/bin/env python3
"""Dọn nhánh git đã merge vào nhánh chính (main).

Hai cách chạy:
  - Làm hook của Claude Code (cờ `--hook`, đọc JSON từ stdin):
      * SessionStart: `git fetch --prune` rồi dọn nhánh cục bộ.
      * PostToolUse (Bash): chỉ chạy sau các lệnh git pull/merge/checkout/switch/fetch hoặc `gh pr merge`.
  - Chạy tay (xem skill clean-merged-branches): `python3 cleanup-merged-branches.py [--dry-run] [--remote] [--fetch]`.

Một nhánh được coi là "đã merge" khi đầu nhánh (tip) là cha thứ hai của một merge commit nằm trên
đường first-parent của origin/<nhánh chính> — tức đã vào main qua PR dạng merge commit (đúng cách repo này merge).
Cố ý KHÔNG dùng `git branch --merged`: nhánh vừa tạo từ main, chưa có commit nào, cũng là tổ tiên của main
và sẽ bị xóa nhầm ngay khi main tiến lên.

An toàn:
  - Không bao giờ xóa main/master/develop, nhánh đang checkout, hay nhánh đang mở ở worktree khác.
  - Mặc định chỉ xóa nhánh CỤC BỘ. Xóa nhánh trên origin cần cờ --remote và chỉ làm khi chạy tay.
  - Nhánh mất upstream ([gone]) nhưng không chứng minh được đã merge (ví dụ squash merge) chỉ được liệt kê, không xóa.
  - Mỗi nhánh đã xóa được in kèm SHA để khôi phục: `git branch <tên> <sha>`.
"""
from __future__ import annotations  # python3 mặc định trên macOS là 3.9; hook crash thì lệnh vẫn chạy (không chặn)

import argparse
import json
import os
import re
import subprocess
import sys

PROTECTED = {"main", "master", "develop"}
GIT_TRIGGER = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?(?:pull|merge|checkout|switch|fetch)\b")
GH_MERGE = re.compile(r"\bgh\s+pr\s+merge\b")


def git(cwd: str, *args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except (subprocess.TimeoutExpired, OSError) as e:
        return subprocess.CompletedProcess(args, 1, "", str(e))


def base_branch(cwd: str) -> str | None:
    r = git(cwd, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if r.returncode == 0 and "/" in r.stdout:
        return r.stdout.strip().split("/", 1)[1]
    for name in ("main", "master"):
        if git(cwd, "rev-parse", "--verify", "-q", f"refs/heads/{name}").returncode == 0:
            return name
    return None


def merged_tips(cwd: str, ref: str) -> set[str]:
    """Đầu của mọi nhánh đã được merge vào `ref` bằng merge commit (cha thứ hai trở đi)."""
    r = git(cwd, "rev-list", "--merges", "--first-parent", "--parents", ref)
    tips: set[str] = set()
    for line in r.stdout.splitlines():
        tips.update(line.split()[2:])
    return tips


def checked_out_branches(cwd: str) -> set[str]:
    r = git(cwd, "worktree", "list", "--porcelain")
    return {ln.split("refs/heads/", 1)[1] for ln in r.stdout.splitlines() if ln.startswith("branch refs/heads/")}


def cleanup(cwd: str, fetch: bool, remote: bool, dry_run: bool) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {"deleted": [], "remote_deleted": [], "gone": [], "skipped": []}
    if git(cwd, "rev-parse", "--git-dir").returncode != 0:
        return result
    if fetch:
        git(cwd, "fetch", "--prune", "origin", timeout=20)
    base = base_branch(cwd)
    if not base:
        return result
    ref = f"origin/{base}" if git(cwd, "rev-parse", "--verify", "-q", f"refs/remotes/origin/{base}").returncode == 0 else base
    tips = merged_tips(cwd, ref)
    current = git(cwd, "branch", "--show-current").stdout.strip()
    busy = checked_out_branches(cwd) | {current, base} | PROTECTED

    fmt = "%(refname:short)\t%(objectname)\t%(upstream:track)"
    for line in git(cwd, "for-each-ref", f"--format={fmt}", "refs/heads").stdout.splitlines():
        name, sha, track = (line.split("\t") + ["", ""])[:3]
        if not name or name in busy:
            continue
        if sha in tips:
            if dry_run:
                result["deleted"].append(f"{name} ({sha[:7]})")
            elif git(cwd, "branch", "-D", name).returncode == 0:
                result["deleted"].append(f"{name} (khôi phục: git branch {name} {sha[:7]})")
            else:
                result["skipped"].append(name)
        elif track == "[gone]":
            result["gone"].append(name)

    if remote:
        fmt = "%(refname:short)\t%(objectname)"
        for line in git(cwd, "for-each-ref", f"--format={fmt}", "refs/remotes/origin").stdout.splitlines():
            full, sha = (line.split("\t") + [""])[:2]
            name = full.split("/", 1)[1] if "/" in full else ""
            if not name or name == "HEAD" or name in PROTECTED or name == base or sha not in tips:
                continue
            if dry_run:
                result["remote_deleted"].append(f"origin/{name} ({sha[:7]})")
            elif git(cwd, "push", "origin", "--delete", name, timeout=30).returncode == 0:
                result["remote_deleted"].append(f"origin/{name} (khôi phục: git push origin {sha[:7]}:refs/heads/{name})")
            else:
                result["skipped"].append(f"origin/{name}")
    return result


def render(result: dict[str, list[str]], dry_run: bool = False) -> str:
    verb = "Sẽ xóa" if dry_run else "Đã xóa"
    parts = []
    if result["deleted"]:
        parts.append(f"{verb} nhánh cục bộ đã merge vào main:\n- " + "\n- ".join(result["deleted"]))
    if result["remote_deleted"]:
        parts.append(f"{verb} nhánh trên origin đã merge vào main:\n- " + "\n- ".join(result["remote_deleted"]))
    if result["gone"]:
        parts.append("Nhánh mất upstream nhưng chưa chứng minh được đã merge (kiểm tra tay rồi mới xóa):\n- " + "\n- ".join(result["gone"]))
    if result["skipped"]:
        parts.append("Không xóa được: " + ", ".join(result["skipped"]))
    return "\n".join(parts)


def hook_mode() -> None:
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return
    event = data.get("hook_event_name")
    cwd = data.get("cwd") or os.getcwd()
    fetch = False
    if event == "SessionStart":
        fetch = True
    elif event == "PostToolUse" and data.get("tool_name") == "Bash":
        cmd = (data.get("tool_input") or {}).get("command", "")
        fetch = bool(GH_MERGE.search(cmd))
        if not (fetch or GIT_TRIGGER.search(cmd)):
            return
    else:
        return
    result = cleanup(cwd, fetch=fetch, remote=False, dry_run=False)
    if result["deleted"]:  # chỉ lên tiếng khi thật sự đã xóa gì đó, tránh nhiễu mỗi lần chạy git
        print(json.dumps({"systemMessage": render(result)}, ensure_ascii=False))


def cli_mode() -> None:
    ap = argparse.ArgumentParser(description="Xóa nhánh đã merge vào nhánh chính.")
    ap.add_argument("--dry-run", action="store_true", help="chỉ liệt kê, không xóa")
    ap.add_argument("--remote", action="store_true", help="xóa cả nhánh tương ứng trên origin")
    ap.add_argument("--fetch", action="store_true", help="chạy git fetch --prune trước")
    args = ap.parse_args()
    out = render(cleanup(os.getcwd(), fetch=args.fetch, remote=args.remote, dry_run=args.dry_run), args.dry_run)
    print(out or "Không có nhánh nào cần dọn.")


if __name__ == "__main__":
    if "--hook" in sys.argv[1:]:
        hook_mode()
    else:
        cli_mode()
