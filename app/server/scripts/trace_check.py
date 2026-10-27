"""S8-10: liệt kê AC trong USER_STORIES.md chưa có test nào gắn mã (pytest marker req / tên test web)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

APP = Path(__file__).resolve().parents[2]
stories = (APP.parent / "docs" / "03-analysis" / "USER_STORIES.md").read_text(encoding="utf-8")
acs = sorted(set(re.findall(r"\*\*(US-\d+-AC\d)\.\*\*", stories)))
found: dict[str, list[str]] = {a: [] for a in acs}
for f in list((APP / "server" / "tests").rglob("test_*.py")) + list((APP / "web" / "src").rglob("*.test.tsx")):
    t = f.read_text(encoding="utf-8")
    for a in set(re.findall(r'req\("(US-\d+-AC\d)"\)', t)) | set(re.findall(r"\[(US-\d+-AC\d)\]", t)):
        found.setdefault(a, []).append(f.name)
    for group in re.findall(r"((?:\[US-\d+-AC\d\])+)", t):
        for a in re.findall(r"US-\d+-AC\d", group):
            if f.name not in found.setdefault(a, []):
                found[a].append(f.name)
# AC không kiểm thử được bằng mã: bằng chứng là tài liệu cấu hình + chữ ký CNTT (S8-07, chờ OQ-005)
NON_CODE = {"US-015-AC1": "phê duyệt vị trí lưu trữ (deploy/DATA_LOCATION.md, chờ OQ-005)"}
missing = [a for a in acs if not found.get(a) and a not in NON_CODE]
for a in acs:
    mark = ("✓ " + ", ".join(sorted(set(found[a])))) if found[a] else ("— " + NON_CODE[a] if a in NON_CODE else "✗ chưa có test")
    print(f"{a:12} {mark}")
tested = sum(1 for a in acs if found.get(a))
print(f"\n{tested}/{len(acs)} AC có test; {len([a for a in acs if a in NON_CODE and not found.get(a)])} AC chỉ có bằng chứng ngoài mã.")
if missing:
    print("Chưa có test:", ", ".join(missing))
    sys.exit(1)
