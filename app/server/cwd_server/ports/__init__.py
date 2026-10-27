"""Cổng (Blueprint §3.2.2). Chỉ chứa hợp đồng, không có cài đặt."""
from __future__ import annotations

from collections.abc import Iterator
from typing import BinaryIO, Protocol

from cwd_server.core.types import Page

Vector = list[float]


class LlmPort(Protocol):
    def embed(self, texts: list[str]) -> list[Vector]: ...

    def generate(self, system: str, user: str, schema: dict) -> dict: ...


class ObjectStorePort(Protocol):
    def put(self, key: str, stream: BinaryIO, size: int) -> None: ...

    def size(self, key: str) -> int: ...

    def get(self, key: str, byte_range: tuple[int, int] | None = None) -> Iterator[bytes]: ...

    def delete(self, key: str) -> None: ...

    def list_keys(self, prefix: str) -> Iterator[tuple[str, float]]:
        """Trả (khóa, thời điểm sửa đổi dạng epoch)."""
        ...

    def check(self) -> None: ...


class PdfExtractorPort(Protocol):
    def extract(self, data: bytes) -> list[Page]: ...
