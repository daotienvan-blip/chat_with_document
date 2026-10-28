"""Kiểm tra tệp tải lên (UC08, S1-01). Thứ tự: thiếu tệp → quá lớn → sai định dạng. Không tin Content-Type."""
from __future__ import annotations

import hashlib
import re
import tempfile
import unicodedata
from dataclasses import dataclass
from typing import IO, BinaryIO

from cwd_server.core.errors import FileTooLarge, InvalidRequest, UnsupportedType

READ_CHUNK = 64 * 1024
SPOOL_MAX = 8 * 1024 * 1024
_BAD = re.compile(r"[\x00-\x1f\x7f/\\]")


@dataclass
class ValidatedUpload:
    name: str
    size: int
    sha256: str
    file: IO[bytes]  # đã tua về đầu


def sanitize_name(filename: str | None) -> str:
    name = unicodedata.normalize("NFC", filename or "")
    name = name.replace("\\", "/").split("/")[-1]
    name = _BAD.sub("", name).strip().strip(".").strip()
    name = name.replace("..", "")
    if not name or name.lower() == "pdf":
        name = "tai-lieu.pdf"
    if len(name) > 255:
        stem, dot, ext = name.rpartition(".")
        name = (stem[: 255 - len(ext) - 1] + "." + ext) if dot and len(ext) <= 10 else name[:255]
    return name


def effective_limit_mb(max_file_size_mb: int | None, hard_max_mb: int) -> int:
    return max_file_size_mb if max_file_size_mb is not None else hard_max_mb


def validate_upload(stream: BinaryIO | None, filename: str | None, limit_mb: int) -> ValidatedUpload:
    if stream is None or not filename:
        raise InvalidRequest("Thiếu tệp tải lên.")
    max_bytes = limit_mb * 1024 * 1024
    h = hashlib.sha256()
    out = tempfile.SpooledTemporaryFile(max_size=SPOOL_MAX)
    size = 0
    head = b""
    while True:
        block = stream.read(READ_CHUNK)
        if not block:
            break
        size += len(block)
        if size > max_bytes:
            out.close()
            raise FileTooLarge(f"Tệp lớn hơn giới hạn {limit_mb} MB.", limit=limit_mb)
        if len(head) < 5:
            head += block[: 5 - len(head)]
        h.update(block)
        out.write(block)
    if size == 0 or not filename.lower().endswith(".pdf") or head != b"%PDF-":
        out.close()
        raise UnsupportedType("Chỉ hỗ trợ tệp PDF.")
    out.seek(0)
    return ValidatedUpload(sanitize_name(filename), size, h.hexdigest(), out)
