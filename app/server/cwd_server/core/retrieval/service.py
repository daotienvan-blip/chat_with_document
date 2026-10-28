"""Truy xuất lai (S3-01): vector + từ khóa, hợp nhất RRF, tối đa N đoạn/tài liệu."""
from __future__ import annotations

from dataclasses import dataclass, replace
from uuid import UUID

from cwd_server.core.text import words
from cwd_server.core.types import RetrievedChunk

MAX_TERMS = 12


def build_tsquery(question: str) -> str:
    """Nối các từ (chữ/số Unicode) bằng OR; không ghép ký tự đặc biệt nào của tsquery."""
    terms: list[str] = []
    for w in words(question):
        w = w.replace("_", "")
        if w and w not in terms:
            terms.append(w)
        if len(terms) >= MAX_TERMS:
            break
    return " | ".join(terms)


def rrf(lists: list[list[RetrievedChunk]], k: int = 60) -> list[RetrievedChunk]:
    scores: dict = {}
    best: dict = {}
    for lst in lists:
        for rank, ch in enumerate(lst, 1):
            scores[ch.chunk_id] = scores.get(ch.chunk_id, 0.0) + 1.0 / (k + rank)
            prev = best.get(ch.chunk_id)
            if prev is None or (prev.vector_score is None and ch.vector_score is not None):
                best[ch.chunk_id] = ch
    merged = [replace(best[cid], score=s) for cid, s in scores.items()]
    merged.sort(key=lambda c: (-c.score, str(c.chunk_id)))
    return merged


def cap_per_document(chunks: list[RetrievedChunk], total: int, per_doc: int) -> list[RetrievedChunk]:
    out: list[RetrievedChunk] = []
    per: dict[UUID, int] = {}
    for ch in chunks:
        if per.get(ch.document_id, 0) >= per_doc:
            continue
        per[ch.document_id] = per.get(ch.document_id, 0) + 1
        out.append(ch)
        if len(out) >= total:
            break
    return out


@dataclass
class RetrievalResult:
    chunks: list[RetrievedChunk]
    top_vector_score: float | None


class RetrievalService:
    def __init__(self, db, chunks_repo, llm, settings):
        self.db, self.repo, self.llm, self.s = db, chunks_repo, llm, settings

    def retrieve(self, question: str) -> RetrievalResult:
        qvec = self.llm.embed([question])[0]
        with self.db.tx() as c:  # tx để SET LOCAL có hiệu lực ở chế độ hnsw
            vec = self.repo.vector_candidates(c, qvec, self.s.rag_top_k_vector, self.s.retrieval_mode,
                                              self.s.hnsw_ef_search)
            fts = self.repo.fts_candidates(c, build_tsquery(question), self.s.rag_top_k_fts)
        top = max((ch.vector_score for ch in vec if ch.vector_score is not None), default=None)
        merged = rrf([vec, fts], self.s.rag_rrf_k)
        return RetrievalResult(cap_per_document(merged, self.s.rag_context_chunks, self.s.rag_max_chunks_per_doc), top)
