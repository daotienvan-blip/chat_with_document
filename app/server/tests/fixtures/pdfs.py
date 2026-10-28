"""Sinh PDF mẫu bằng mã (không commit tệp nhị phân). Font hệ thống có dấu tiếng Việt nếu có."""
from __future__ import annotations

import os

import pymupdf

FONT_CANDIDATES = ["/System/Library/Fonts/Supplemental/Arial.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
FONT = next((f for f in FONT_CANDIDATES if os.path.exists(f)), None)


def _insert(page, text: str) -> None:
    rect = pymupdf.Rect(50, 50, 545, 800)
    if not FONT and not text.isascii():
        # font mặc định không có dấu tiếng Việt ⇒ chữ thành "?" và test hỏng âm thầm
        raise RuntimeError("Thiếu font có dấu tiếng Việt cho PDF test: cài fonts-dejavu-core")
    if FONT:
        page.insert_textbox(rect, text, fontsize=11, fontfile=FONT, fontname="F0")
    else:
        page.insert_textbox(rect, text, fontsize=11)


def text_pdf(pages: list[str]) -> bytes:
    doc = pymupdf.open()
    for t in pages:
        _insert(doc.new_page(), t)
    return doc.tobytes()


def encrypted_pdf() -> bytes:
    doc = pymupdf.open()
    _insert(doc.new_page(), "Nội dung bí mật")
    return doc.tobytes(encryption=pymupdf.PDF_ENCRYPT_AES_256, owner_pw="o", user_pw="u")


def corrupt_pdf() -> bytes:
    return text_pdf(["Tệp sẽ bị cắt cụt"])[:200]


def image_only_pdf() -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 40, 40), False)
    pix.clear_with(200)
    page.insert_image(pymupdf.Rect(50, 50, 250, 250), pixmap=pix)
    return doc.tobytes()


def token_pages_pdf(n: int = 6) -> bytes:
    """Mỗi trang chứa token duy nhất ZXQ<k>; trang 3–4 có một câu dài vắt qua ranh giới (S4-01)."""
    pages = []
    for k in range(1, n + 1):
        filler = " ".join(f"tu{k}x{i}" for i in range(40))
        pages.append(f"Trang {k}. Mã kiểm tra ZXQ{k} xuất hiện ở đây. {filler}")
    return text_pdf(pages)
