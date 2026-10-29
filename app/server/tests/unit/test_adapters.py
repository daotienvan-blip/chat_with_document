"""Adapter: AI cục bộ, HTTP (MockTransport), chịu lỗi, kho bộ nhớ, trích PDF."""
from __future__ import annotations

import io
import json
import logging

import httpx
import pytest

from cwd_server.adapters.llm_http import HttpLlm
from cwd_server.adapters.llm_local import ExtractiveLlm, FakeLlm
from cwd_server.adapters.pymupdf_extractor import PyMuPdfExtractor
from cwd_server.adapters.resilient_llm import CircuitBreaker, ResilientLlm
from cwd_server.adapters.stores import InMemoryObjectStore
from cwd_server.core.answer.prompt import LLM_OUTPUT_SCHEMA
from cwd_server.core.errors import (
    AiBadOutput,
    AiTimeout,
    AiUnavailable,
    ConfigurationError,
    PdfCorrupt,
    PdfEncrypted,
)
from tests.fixtures import pdfs


def _cos(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True))


def test_hash_embedding_similarity():
    llm = FakeLlm(128)
    q, near, far = llm.embed(["điều khoản thanh toán", "Điều khoản thanh toán trong 30 ngày", "giao hàng cảng"])
    assert _cos(q, near) > _cos(q, far)
    assert llm.embed(["x y"]) == llm.embed(["x y"])
    nodia = llm.embed(["dieu khoan thanh toan"])[0]
    assert _cos(q, nodia) > 0.3  # bản không dấu vẫn gần


def test_extractive_cites_and_not_found():
    llm = ExtractiveLlm(64)
    user = ('<cau_hoi>\nThời hạn thanh toán là bao nhiêu ngày?\n</cau_hoi>\n<tai_lieu>\n'
            '<doan id="c1" tai_lieu="a.pdf" trang="1-1">\nGiao hàng tại kho. Thời hạn thanh toán là 30 ngày.\n</doan>\n'
            '<doan id="c2" tai_lieu="b.pdf" trang="2-2">\nBảo hành 12 tháng.\n</doan>\n</tai_lieu>')
    out = llm.generate("", user, LLM_OUTPUT_SCHEMA)
    assert out["status"] in ("answered", "partial") and out["citations"] == ["c1"]
    assert "30 ngày" in out["answer"]
    out2 = llm.generate("", user.replace("Thời hạn thanh toán là bao nhiêu ngày?", "Giá cổ phiếu hôm nay?"),
                        LLM_OUTPUT_SCHEMA)
    assert out2 == {"status": "not_found", "answer": "", "citations": []}


@pytest.mark.req("US-010-AC1")
def test_extractive_accents_def001():
    """DEF-001: câu có dấu không được khớp "tỷ"≡"ty", "đã"≡"đà"; câu gõ không dấu vẫn tìm được văn bản có dấu."""
    llm = ExtractiveLlm(64)
    ctx = ('<tai_lieu>\n<doan id="c1" tai_lieu="c.pdf" trang="1-1">\nMục 1. Nhân viên đi công tác được thanh toán '
           'chi phí đi lại theo hóa đơn thực tế.\n</doan>\n<doan id="c2" tai_lieu="a.pdf" trang="1-1">\nĐiều 2. Giá '
           'trị hợp đồng. Tổng giá trị hợp đồng là 1,2 tỷ đồng, đã bao gồm thuế giá trị gia tăng.\n</doan>\n</tai_lieu>')

    def ask(q):
        return llm.generate("", f"<cau_hoi>\n{q}\n</cau_hoi>\n{ctx}", LLM_OUTPUT_SCHEMA)

    assert ask("Công ty có bao nhiêu nhân viên ở chi nhánh Đà Nẵng?")["status"] == "not_found"
    out = ask("gia tri hop dong la bao nhieu?")
    assert out["status"] == "answered" and out["citations"] == ["c2"]


def _http(handler):
    return HttpLlm("http://ai.local/v1", "sk-secret", "emb", "chat", dim=3, transport=httpx.MockTransport(handler))


def test_http_llm_ok_and_dim_check(caplog):
    def h(req):
        body = json.loads(req.content)
        if req.url.path.endswith("/embeddings"):
            return httpx.Response(200, json={"data": [{"index": i, "embedding": [0.1, 0.2, 0.3]}
                                                      for i, _ in enumerate(body["input"])]})
        assert body["temperature"] == 0
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(
            {"status": "answered", "answer": "x", "citations": ["c1"]})}}]})
    caplog.set_level(logging.DEBUG)
    llm = _http(h)
    assert llm.embed(["a", "b"]) == [[0.1, 0.2, 0.3]] * 2
    assert llm.generate("s", "u", LLM_OUTPUT_SCHEMA)["status"] == "answered"
    assert "sk-secret" not in caplog.text
    bad = HttpLlm("http://ai.local/v1", None, "e", "c", dim=4, transport=httpx.MockTransport(h))
    with pytest.raises(ConfigurationError):
        bad.embed(["a"])


@pytest.mark.parametrize("resp,exc", [(503, AiUnavailable), (429, AiUnavailable), (400, ConfigurationError),
                                      ("timeout", AiTimeout), ("conn", AiUnavailable), ("garbage", AiBadOutput)])
def test_http_llm_errors(resp, exc):
    def h(req):
        if resp == "timeout":
            raise httpx.ReadTimeout("t")
        if resp == "conn":
            raise httpx.ConnectError("c")
        if resp == "garbage":
            return httpx.Response(200, json={"choices": [{"message": {"content": "không phải json"}}]})
        return httpx.Response(resp, json={})
    with pytest.raises(exc):
        _http(h).generate("s", "u", LLM_OUTPUT_SCHEMA)


def test_resilient_retry_then_breaker():
    now = [0.0]
    calls = {"n": 0}

    class Flaky:
        fail = True

        def embed(self, texts):
            calls["n"] += 1
            if Flaky.fail:
                raise AiUnavailable()
            return [[1.0]]

        def generate(self, *a):
            raise AiTimeout()
    sleeps = []
    r = ResilientLlm(Flaky(), CircuitBreaker(5, 30, clock=lambda: now[0]), sleep=sleeps.append)
    with pytest.raises(AiUnavailable):
        r.embed(["x"])
    assert calls["n"] == 3 and len(sleeps) == 2 and sleeps[1] > sleeps[0] * 1.2  # 2 lần thử lại, lùi lũy thừa
    with pytest.raises(AiTimeout):
        r.generate("s", "u", {})  # 1 lần thử lại ⇒ tổng 5 lỗi liên tiếp
    assert r.breaker.state == "open"
    n = calls["n"]
    with pytest.raises(AiUnavailable) as e:
        r.embed(["x"])
    assert e.value.breaker_open and calls["n"] == n  # mở: không gọi dịch vụ
    now[0] += 31
    Flaky.fail = False
    assert r.embed(["x"]) == [[1.0]] and r.breaker.state == "closed"


def test_memory_store_range_and_delete():
    s = InMemoryObjectStore()
    key = "documents/00000000-0000-0000-0000-000000000001.pdf"
    s.put(key, io.BytesIO(b"0123456789"), 10)
    assert b"".join(s.get(key, (2, 4))) == b"234"
    s.delete(key)
    s.delete(key)
    with pytest.raises(ValueError):
        s.put("../x.pdf", io.BytesIO(b""), 0)


@pytest.mark.req("US-003-AC1")
@pytest.mark.req("US-003-AC2")
@pytest.mark.req("US-003-AC3")
def test_pdf_extractor_cases():
    ex = PyMuPdfExtractor(timeout_s=30)
    pages = ex.extract(pdfs.token_pages_pdf(3))
    assert [p.number for p in pages] == [1, 2, 3] and "ZXQ2" in pages[1].text
    vi = ex.extract(pdfs.text_pdf(["Điều khoản thanh toán trong vòng 30 ngày."]))
    assert "Điều khoản thanh toán" in vi[0].text
    with pytest.raises(PdfEncrypted):
        ex.extract(pdfs.encrypted_pdf())
    with pytest.raises(PdfCorrupt):
        ex.extract(pdfs.corrupt_pdf())
    assert all(not p.text.strip() for p in ex.extract(pdfs.image_only_pdf()))
