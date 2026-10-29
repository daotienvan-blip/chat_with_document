"""LlmPort chạy cục bộ, không cần mạng.

- `HashEmbedder`: băm từng từ (có dấu và không dấu, cả cặp từ) vào vector D chiều rồi chuẩn hóa; độ tương tự cosin
  phản ánh mức trùng từ. Dùng cho kiểm thử và bản demo.
- `FakeLlm`: `generate` trả kịch bản do test đặt, có thể gây lỗi theo yêu cầu (S0-05).
- `ExtractiveLlm`: AI giả trích xuất cho bản demo — chọn câu trong các đoạn được cung cấp có nhiều từ khóa của câu
  hỏi nhất, trích dẫn đúng mã đoạn. Không sinh nội dung mới, nên không thay thế được mô hình thật về chất lượng.
"""
from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Callable

from cwd_server.core.errors import AiBadOutput, AiTimeout, AiUnavailable
from cwd_server.core.text import keywords, strip_accents, words


class HashEmbedder:
    def __init__(self, dim: int):
        self.dim = dim

    def _features(self, text: str) -> list[str]:
        ws = words(text)
        feats = ws + [strip_accents(w) for w in ws]
        feats += [f"{a}_{b}" for a, b in zip(ws, ws[1:], strict=False)]
        return feats

    def embed_one(self, text: str) -> list[float]:
        v = [0.0] * self.dim
        for f in self._features(text):
            h = hashlib.blake2b(f.encode("utf-8"), digest_size=8).digest()
            idx = int.from_bytes(h[:4], "little") % self.dim
            v[idx] += 1.0 if h[4] & 1 else -1.0
        n = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / n for x in v]

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_one(t) for t in texts]


class FakeLlm(HashEmbedder):
    """generate trả lần lượt các phần tử của `script` (dict, Exception, hoặc hàm (system,user)->dict)."""

    def __init__(self, dim: int, script: list | None = None):
        super().__init__(dim)
        self.script: list = list(script or [])
        self.generate_calls = 0
        self.embed_calls = 0
        self.embed_error: Exception | None = None
        self.last_user: str | None = None

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.embed_calls += 1
        if self.embed_error:
            raise self.embed_error
        return super().embed(texts)

    def generate(self, system: str, user: str, schema: dict) -> dict:
        self.generate_calls += 1
        self.last_user = user
        if not self.script:
            return {"status": "not_found", "answer": "", "citations": []}
        item = self.script.pop(0) if len(self.script) > 1 else self.script[0]
        if isinstance(item, Exception):
            raise item
        if callable(item):
            return item(system, user)
        return item


_DOAN_RE = re.compile(r'<doan id="(c\d+)"[^>]*>\n?(.*?)\n?</doan>', re.S)
_Q_RE = re.compile(r"<cau_hoi>\n?(.*?)\n?</cau_hoi>", re.S)
_SENT_RE = re.compile(r"(?<=[.!?;])\s+|\n+")
MIN_SENT_WORDS = 8


def sentences(body: str) -> list[str]:
    """Tách câu; mảnh ngắn (tiêu đề như "Điều 3.") được ghép vào câu kế tiếp để câu trả lời có nội dung."""
    out, buf = [], ""
    for part in _SENT_RE.split(body):
        part = " ".join(part.split())
        if not part:
            continue
        buf = f"{buf} {part}".strip()
        if len(buf.split()) >= MIN_SENT_WORDS:
            out.append(buf)
            buf = ""
    if buf:
        out.append(buf)
    return out


class ExtractiveLlm(HashEmbedder):
    """Chọn câu tham lam: mỗi bước lấy câu bổ sung nhiều trọng số từ khóa mới nhất (từ hiếm nặng hơn).
    Độ phủ = tổng trọng số từ khóa đã phủ / tổng trọng số từ khóa câu hỏi.
    ≥ answered_at ⇒ answered; ≥ partial_at ⇒ partial (kèm câu nêu phần thiếu); còn lại ⇒ not_found."""

    def __init__(self, dim: int, max_sentences: int = 4, answered_at: float = 0.6, partial_at: float = 0.4):
        super().__init__(dim)
        self.max_sentences, self.answered_at, self.partial_at = max_sentences, answered_at, partial_at

    def generate(self, system: str, user: str, schema: dict) -> dict:
        qm = _Q_RE.search(user)
        if not qm:
            raise AiBadOutput("thiếu câu hỏi")
        q_text = qm.group(1)
        q_kw = keywords(q_text)
        none = {"status": "not_found", "answer": "", "citations": []}
        if not q_kw:
            return none
        # Câu hỏi có dấu ⇒ so khớp đúng dấu ("tỷ" ≠ "ty", "đã" ≠ "đà" — DEF-001); chỉ bỏ dấu khi người dùng gõ không dấu.
        fuzzy = strip_accents(q_text) == q_text
        sents: list[tuple[str, str, set[str]]] = []  # (mã đoạn, câu, từ khóa trúng)
        for cid, body in _DOAN_RE.findall(user):
            for sent in sentences(body):
                sw = set(words(sent))
                if fuzzy:
                    sw |= {strip_accents(w) for w in sw}
                hit = {w for w in q_kw if w in sw}
                if hit:
                    sents.append((cid, sent, hit))
        if not sents:
            return none
        n = len(sents)
        df = {k: sum(1 for _, _, h in sents if k in h) for k in q_kw}
        weight = {k: math.log(1 + (n + 1) / (df[k] + 0.5)) for k in q_kw}
        total = sum(weight.values())
        covered: set[str] = set()
        picked: list[tuple[str, str]] = []
        while len(picked) < self.max_sentences:
            best = max(sents, key=lambda x: (sum(weight[k] for k in x[2] - covered), -len(x[1])))
            gain = sum(weight[k] for k in best[2] - covered)
            if gain < 0.15 * total or (best[0], best[1]) in picked:
                break
            picked.append((best[0], best[1]))
            covered |= best[2]
        cov = sum(weight[k] for k in covered) / total
        if cov < self.partial_at or not picked:
            return none
        cites = list(dict.fromkeys(cid for cid, _ in picked))
        answer = " ".join(sent for _, sent in picked)
        if cov < self.answered_at:
            return {"status": "partial", "citations": cites,
                    "answer": answer + " Một phần câu hỏi không tìm thấy trong các tài liệu đã tải."}
        return {"status": "answered", "answer": answer, "citations": cites}


def failing(exc_factory: Callable[[], Exception]) -> Callable:
    def f(system: str, user: str) -> dict:
        raise exc_factory()
    return f


__all__ = ["HashEmbedder", "FakeLlm", "ExtractiveLlm", "AiUnavailable", "AiTimeout", "failing"]
