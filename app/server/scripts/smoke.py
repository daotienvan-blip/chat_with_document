"""Kiểm tra khói đầu-cuối trên hệ thống đang chạy (thay cho Playwright E2E khi chưa có trình duyệt tự động).

Hành trình: tải PDF → chờ sẵn sàng → hỏi (có nguồn) → mở nguồn đúng trang → câu ngoài tài liệu → tệp lỗi → xóa.
Chạy: python scripts/smoke.py http://localhost:8000 ../samples
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import httpx

base, samples = sys.argv[1], Path(sys.argv[2])
c = httpx.Client(base_url=base, timeout=60, verify=os.environ.get("SMOKE_CA", True))  # SMOKE_CA: chứng chỉ tự ký
ok = 0


def check(cond: bool, msg: str) -> None:
    global ok
    print(("  ✓ " if cond else "  ✗ ") + msg)
    if not cond:
        sys.exit(1)
    ok += 1


def up(name: str) -> dict:
    r = c.post("/api/v1/documents", files={"file": (name, (samples / name).read_bytes(), "application/pdf")})
    return {"status_code": r.status_code, **r.json()}


def wait(doc_id: str) -> dict:
    for _ in range(120):
        d = c.get(f"/api/v1/documents/{doc_id}").json()
        if d["status"] != "processing":
            return d
        time.sleep(0.5)
    raise SystemExit("quá thời gian chờ xử lý")


print("Kiểm tra khói", base)
check(c.get("/readyz").text == "ok", "readyz")
check(c.get("/").status_code == 200 and "<div id=\"root\">" in c.get("/").text, "phục vụ giao diện web")
ids = {}
for name in ("hop-dong-A.pdf", "bao-gia-B.pdf", "quy-dinh-C.pdf"):
    r = up(name)
    check(r["status_code"] == 202 and r["status"] == "processing", f"tải lên {name} → 202 processing")
    ids[name] = r["id"]
for name, i in ids.items():
    d = wait(i)
    check(d["status"] == "ready" and d["pageCount"], f"{name} sẵn sàng ({d['pageCount']} trang)")

a = c.post("/api/v1/questions", json={"question": "Điều khoản thanh toán của hợp đồng A là gì?"}).json()
check(a["status"] in ("answered", "partial") and a["sources"], f"hỏi có căn cứ → {a['status']}")
src = a["sources"][0]
check(src["documentName"] == "hop-dong-A.pdf" and src["pages"], f"nguồn: {src['documentName']} tr. {src['pages']}")
print("     câu trả lời:", a["answer"][:140])
f = c.get(f"/api/v1/documents/{src['documentId']}/file", headers={"Range": "bytes=0-4"})
check(f.status_code == 206 and f.content == b"%PDF-", "mở tài liệu nguồn (Range)")

m = c.post("/api/v1/questions", json={"question": "So sánh thời hạn giao hàng giữa hợp đồng A và báo giá B"}).json()
check(m["status"] != "not_found", f"câu hỏi nhiều tài liệu → {m['status']}, nguồn {[s['documentName'] for s in m['sources']]}")

n = c.post("/api/v1/questions", json={"question": "Giá cổ phiếu Apple hôm nay bao nhiêu?"}).json()
check(n["status"] == "not_found" and n["sources"] == [], "câu ngoài tài liệu → not_found, không nguồn")

r = up("co-mat-khau.pdf")
check(wait(r["id"])["failureReason"] == "FILE_ENCRYPTED", "PDF có mật khẩu → FILE_ENCRYPTED")
bad = c.post("/api/v1/documents", files={"file": ("khong-phai-pdf.txt", b"hello", "text/plain")})
check(bad.status_code == 400 and bad.json()["code"] == "UNSUPPORTED_TYPE", "tệp không phải PDF → 400 UNSUPPORTED_TYPE")

check(c.delete(f"/api/v1/documents/{ids['quy-dinh-C.pdf']}").status_code == 204, "xóa quy-dinh-C.pdf → 204")
q = c.post("/api/v1/questions", json={"question": "Phụ cấp lưu trú công tác phí là bao nhiêu?"}).json()
check(all(s["documentName"] != "quy-dinh-C.pdf" for s in q["sources"]), "sau khi xóa, không còn nguồn từ tài liệu đã xóa")
c.delete(f"/api/v1/documents/{r['id']}")
print(f"\nĐạt {ok} kiểm tra.")
