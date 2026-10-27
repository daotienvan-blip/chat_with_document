"""Tiện ích văn bản thuần (không I/O): tách từ, bỏ dấu tiếng Việt, từ dừng."""
from __future__ import annotations

import re
import unicodedata

WORD_RE = re.compile(r"\w+", re.UNICODE)

# Từ dừng tối thiểu (tiếng Việt + tiếng Anh) để chấm điểm trích xuất; không dùng cho FTS.
STOPWORDS = {
    "là", "gì", "của", "và", "các", "những", "có", "không", "được", "cho", "trong", "với", "này", "đó", "thì",
    "mà", "ở", "một", "theo", "về", "khi", "nào", "bao", "nhiêu", "như", "thế", "tại", "sao", "hay", "hoặc",
    "đã", "sẽ", "bị", "từ", "đến", "ra", "vào", "lên", "do", "để", "nếu", "cũng", "rất", "nhé", "ạ", "ai",
    "the", "a", "an", "of", "and", "or", "is", "are", "what", "which", "to", "in", "on", "for", "with", "how",
}


def strip_accents(s: str) -> str:
    s = s.replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def words(text: str) -> list[str]:
    return WORD_RE.findall(unicodedata.normalize("NFC", text).lower())


def keywords(text: str) -> list[str]:
    seen: list[str] = []
    for w in words(text):
        if w not in STOPWORDS and w not in seen:
            seen.append(w)
    return seen
