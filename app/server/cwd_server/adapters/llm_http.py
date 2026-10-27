"""LlmPort qua HTTP, giao thức tương thích OpenAI (S3-04) `[Đề xuất]`.

Nhà cung cấp thật chờ OQ-005 / OQ-S01 — không dùng cho dữ liệu thật trước khi CNTT phê duyệt.
Không bao giờ ghi thân yêu cầu/phản hồi hay khóa API vào log.
"""
from __future__ import annotations

import json

import httpx

from cwd_server.core.errors import AiBadOutput, AiTimeout, AiUnavailable, ConfigurationError


class HttpLlm:
    def __init__(self, base_url: str, api_key: str | None, embed_model: str, chat_model: str, dim: int,
                 temperature: float = 0.0, embed_timeout: float = 10.0, generate_timeout: float = 30.0,
                 transport: httpx.BaseTransport | None = None):
        if not base_url or not embed_model or not chat_model:
            raise ConfigurationError("thiếu LLM_BASE_URL / LLM_EMBED_MODEL / LLM_CHAT_MODEL")
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self.client = httpx.Client(base_url=base_url.rstrip("/"), headers=headers, transport=transport)
        self.embed_model, self.chat_model, self.dim = embed_model, chat_model, dim
        self.temperature = temperature
        self.embed_timeout, self.generate_timeout = embed_timeout, generate_timeout

    def _post(self, path: str, body: dict, timeout: float) -> dict:
        try:
            r = self.client.post(path, json=body, timeout=timeout)
        except httpx.TimeoutException as e:
            raise AiTimeout() from e
        except httpx.HTTPError as e:
            raise AiUnavailable() from e
        if r.status_code == 429 or r.status_code >= 500:
            raise AiUnavailable()
        if r.status_code >= 400:
            raise ConfigurationError(f"dịch vụ AI từ chối yêu cầu (HTTP {r.status_code})")
        return r.json()

    def embed(self, texts: list[str]) -> list[list[float]]:
        data = self._post("/embeddings", {"model": self.embed_model, "input": texts}, self.embed_timeout)
        vecs = [d["embedding"] for d in sorted(data["data"], key=lambda d: d["index"])]
        if vecs and len(vecs[0]) != self.dim:
            raise ConfigurationError(f"số chiều embedding {len(vecs[0])} ≠ EMBEDDING_DIM {self.dim}")
        return vecs

    def generate(self, system: str, user: str, schema: dict) -> dict:
        data = self._post("/chat/completions", {
            "model": self.chat_model, "temperature": self.temperature,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_schema",
                                "json_schema": {"name": "answer", "schema": schema, "strict": True}},
        }, self.generate_timeout)
        try:
            return json.loads(data["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
            raise AiBadOutput() from e
