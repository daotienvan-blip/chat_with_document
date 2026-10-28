"""PdfExtractorPort bằng PyMuPDF, chạy trong tiến trình con có hạn thời gian và bộ nhớ (S2-01).

PDF tải lên là đầu vào không tin cậy: trình phân tích chạy tách khỏi worker để không làm treo hay cạn bộ nhớ.
Giới hạn bộ nhớ (RLIMIT_AS) có thể không áp dụng trên macOS; hãy kiểm tra trên Linux/container.
Lưu ý giấy phép: PyMuPDF dùng AGPL/thương mại [Unverified — cần kiểm tra với pháp lý]; lõi chỉ thấy PdfExtractorPort.
"""
from __future__ import annotations

import json
import subprocess
import sys
import unicodedata

from cwd_server.core.errors import PdfCorrupt, PdfEncrypted, PdfTimeout
from cwd_server.core.types import Page

EXIT_ENCRYPTED = 10
EXIT_CORRUPT = 11


def _child_main() -> None:  # chạy trong tiến trình con
    import resource

    mem_mb = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
    try:
        resource.setrlimit(resource.RLIMIT_AS, (mem_mb * 1024 * 1024, mem_mb * 1024 * 1024))
    except (ValueError, OSError):
        pass
    import pymupdf

    data = sys.stdin.buffer.read()
    try:
        doc = pymupdf.open(stream=data, filetype="pdf")
    except Exception:
        sys.exit(EXIT_CORRUPT)
    if doc.needs_pass:
        sys.exit(EXIT_ENCRYPTED)
    try:
        pages = [{"n": i + 1, "t": doc[i].get_text("text")} for i in range(doc.page_count)]
    except Exception:
        sys.exit(EXIT_CORRUPT)
    if not pages:
        sys.exit(EXIT_CORRUPT)
    sys.stdout.write(json.dumps(pages, ensure_ascii=False))


class PyMuPdfExtractor:
    def __init__(self, timeout_s: float = 120.0, memory_mb: int = 1024):
        self.timeout_s = timeout_s
        self.memory_mb = memory_mb

    def extract(self, data: bytes) -> list[Page]:
        try:
            r = subprocess.run(
                [sys.executable, "-c", "from cwd_server.adapters.pymupdf_extractor import _child_main; _child_main()",
                 str(self.memory_mb)],
                input=data, capture_output=True, timeout=self.timeout_s)
        except subprocess.TimeoutExpired as e:
            raise PdfTimeout("quá thời gian trích văn bản") from e
        if r.returncode == EXIT_ENCRYPTED:
            raise PdfEncrypted()
        if r.returncode != 0:
            raise PdfCorrupt()
        # NFKC: đổi khoảng trắng không ngắt (\xa0) và ký tự tương thích về dạng thường để tách từ/FTS đúng
        return [Page(p["n"], unicodedata.normalize("NFKC", p["t"]).replace("\u00ad", "-"))  # gạch nối mềm
                for p in json.loads(r.stdout.decode("utf-8"))]
