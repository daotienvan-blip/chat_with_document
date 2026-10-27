"""Chia đoạn (S2-02): ~N từ mỗi đoạn, chồng lấp, giữ biên trang. Đếm từ là xấp xỉ token [Đề xuất]."""
from __future__ import annotations

from cwd_server.core.types import ChunkDraft, Page


class Chunker:
    def __init__(self, chunk_tokens: int = 600, overlap: int = 100, max_chars: int = 8000):
        if not 0 <= overlap < chunk_tokens:
            raise ValueError("overlap phải nhỏ hơn chunk_tokens")
        self.size, self.overlap, self.max_chars = chunk_tokens, overlap, max_chars

    def split(self, pages: list[Page]) -> list[ChunkDraft]:
        stream: list[tuple[str, int]] = [(w, p.number) for p in pages for w in p.text.split()]
        out: list[ChunkDraft] = []
        i = 0
        while i < len(stream):
            window = stream[i:i + self.size]
            # trần độ dài ký tự (bảo vệ tsvector): cắt bớt từ cuối nếu vượt
            while len(window) > 1 and sum(len(w) + 1 for w, _ in window) > self.max_chars:
                window = window[: max(1, len(window) * 3 // 4)]
            text = " ".join(w for w, _ in window)
            out.append(ChunkDraft(len(out), window[0][1], window[-1][1], text))
            if i + len(window) >= len(stream):
                break
            # bước tiến giữ đúng `overlap` từ chồng lấp, kể cả khi cửa sổ bị cắt bớt vì trần ký tự
            i += max(1, len(window) - self.overlap) if len(window) > self.overlap else len(window)
        return out
