"""AnswerService (S3-03, S5-01): G-L1 → LLM → G-L2 → nguồn từ siêu dữ liệu (G-L3)."""
from __future__ import annotations

import logging

from cwd_server.core.answer.prompt import LLM_OUTPUT_SCHEMA, build_messages, parse_output, validate
from cwd_server.core.errors import AiBadOutput
from cwd_server.core.types import AnswerResult, AnswerStatus, SourceRef

NOT_FOUND_MESSAGE = "Không tìm thấy thông tin trong các tài liệu đã tải."
log = logging.getLogger("cwd.answer")


class AnswerService:
    def __init__(self, db, chunks_repo, retrieval, llm, min_relevance: float = 0.0, on_status=None,
                 on_downgrade=None):
        self.db, self.repo, self.retrieval, self.llm = db, chunks_repo, retrieval, llm
        self.min_relevance = min_relevance
        self.on_status = on_status or (lambda s: None)
        self.on_downgrade = on_downgrade or (lambda: None)

    def _not_found(self) -> AnswerResult:
        self.on_status(AnswerStatus.NOT_FOUND)
        return AnswerResult(AnswerStatus.NOT_FOUND, NOT_FOUND_MESSAGE, [])

    def ask(self, question: str) -> AnswerResult:
        r = self.retrieval.retrieve(question)
        # G-L1: không có căn cứ ⇒ không gọi LLM
        if not r.chunks or (r.top_vector_score is not None and r.top_vector_score < self.min_relevance):
            return self._not_found()
        system, user, mapping = build_messages(question, r.chunks)
        out = None
        for _ in range(2):  # đầu ra sai schema: thử lại 1 lần
            try:
                out = parse_output(self.llm.generate(system, user, LLM_OUTPUT_SCHEMA))
                break
            except AiBadOutput:
                continue
        if out is None:
            return self._not_found()
        v = validate(out, mapping)  # G-L2
        if v.downgraded:
            self.on_downgrade()
        if v.status == AnswerStatus.NOT_FOUND:
            return self._not_found()
        # G-L3: tra lại đoạn (lọc searchable) để lấy tên + trang từ CSDL, không từ văn bản LLM
        with self.db.read() as c:
            fresh = {ch.chunk_id: ch for ch in self.repo.by_ids(c, [ch.chunk_id for ch in v.cited])}
        if not fresh:
            return self._not_found()  # tài liệu vừa bị xóa
        order: list = []
        pages: dict = {}
        names: dict = {}
        for ch in v.cited:  # giữ thứ tự trích dẫn (liên quan nhất trước)
            f = fresh.get(ch.chunk_id)
            if f is None:
                continue
            if f.document_id not in pages:
                order.append(f.document_id)
                pages[f.document_id] = set()
                names[f.document_id] = f.document_name
            pages[f.document_id].update(range(f.page_start, f.page_end + 1))
        sources = [SourceRef(d, names[d], sorted(pages[d])) for d in order]
        self.on_status(v.status)
        return AnswerResult(v.status, v.answer, sources)
