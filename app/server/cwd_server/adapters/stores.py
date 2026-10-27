"""Cài đặt ObjectStorePort: bộ nhớ (test) và hệ tệp cục bộ (demo, thay MinIO khi không có Docker)."""
from __future__ import annotations

import os
import re
import shutil
import threading
import time
from collections.abc import Iterator
from pathlib import Path
from typing import BinaryIO

from cwd_server.core.errors import StorageUnavailable

KEY_RE = re.compile(r"^documents/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.pdf$")
CHUNK = 64 * 1024


def check_key(key: str) -> str:
    if not KEY_RE.match(key):
        raise ValueError("khóa lưu trữ không hợp lệ")
    return key


class InMemoryObjectStore:
    def __init__(self) -> None:
        self._data: dict[str, tuple[bytes, float]] = {}
        self._lock = threading.Lock()
        self.fail_next: Exception | None = None  # dùng trong test chèn lỗi

    def _maybe_fail(self) -> None:
        if self.fail_next:
            e, self.fail_next = self.fail_next, None
            raise e

    def put(self, key: str, stream: BinaryIO, size: int) -> None:
        self._maybe_fail()
        check_key(key)
        with self._lock:
            self._data[key] = (stream.read(), time.time())

    def size(self, key: str) -> int:
        self._maybe_fail()
        if key not in self._data:
            raise FileNotFoundError(key)
        return len(self._data[key][0])

    def get(self, key: str, byte_range: tuple[int, int] | None = None) -> Iterator[bytes]:
        self._maybe_fail()
        if key not in self._data:
            raise FileNotFoundError(key)
        data = self._data[key][0]
        if byte_range:
            data = data[byte_range[0]:byte_range[1] + 1]
        for i in range(0, len(data), CHUNK):
            yield data[i:i + CHUNK]

    def delete(self, key: str) -> None:
        self._maybe_fail()
        with self._lock:
            self._data.pop(key, None)

    def list_keys(self, prefix: str) -> Iterator[tuple[str, float]]:
        for k, (_, ts) in list(self._data.items()):
            if k.startswith(prefix):
                yield k, ts

    def check(self) -> None:
        self._maybe_fail()


class LocalFsObjectStore:
    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.root / check_key(key)

    def put(self, key: str, stream: BinaryIO, size: int) -> None:
        p = self._path(key)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            tmp = p.with_suffix(".part")
            with open(tmp, "wb") as f:
                shutil.copyfileobj(stream, f, CHUNK)
            os.replace(tmp, p)
        except OSError as e:
            raise StorageUnavailable() from e

    def size(self, key: str) -> int:
        try:
            return self._path(key).stat().st_size
        except FileNotFoundError:
            raise
        except OSError as e:
            raise StorageUnavailable() from e

    def get(self, key: str, byte_range: tuple[int, int] | None = None) -> Iterator[bytes]:
        p = self._path(key)
        if not p.exists():
            raise FileNotFoundError(key)

        def gen() -> Iterator[bytes]:
            with open(p, "rb") as f:
                start, end = byte_range if byte_range else (0, p.stat().st_size - 1)
                f.seek(start)
                left = end - start + 1
                while left > 0:
                    b = f.read(min(CHUNK, left))
                    if not b:
                        break
                    left -= len(b)
                    yield b
        return gen()

    def delete(self, key: str) -> None:
        try:
            self._path(key).unlink(missing_ok=True)
        except OSError as e:
            raise StorageUnavailable() from e

    def list_keys(self, prefix: str) -> Iterator[tuple[str, float]]:
        base = self.root / "documents"
        if not base.exists():
            return
        for p in base.glob("*.pdf"):
            key = f"documents/{p.name}"
            if key.startswith(prefix):
                yield key, p.stat().st_mtime

    def check(self) -> None:
        if not self.root.is_dir() or not os.access(self.root, os.W_OK):
            raise StorageUnavailable()
