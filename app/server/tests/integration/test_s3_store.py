"""S0-06: S3ObjectStore trên dịch vụ S3 thật của `make up` (SeaweedFS, cổng 9000).

Bỏ qua khi không có boto3 hoặc dịch vụ S3 không chạy. Đổi đích bằng S3_TEST_ENDPOINT.
"""
from __future__ import annotations

import io
import os
import socket
import uuid
from urllib.parse import urlparse

import pytest

from cwd_server.core.errors import StorageUnavailable

pytestmark = pytest.mark.integration
ENDPOINT = os.environ.get("S3_TEST_ENDPOINT", "http://localhost:9000")


def _reachable(url: str) -> bool:
    u = urlparse(url)
    try:
        socket.create_connection((u.hostname, u.port or 80), timeout=1).close()
        return True
    except OSError:
        return False


@pytest.fixture(scope="module")
def store():
    pytest.importorskip("boto3")
    if not _reachable(ENDPOINT):
        pytest.skip(f"không có S3 tại {ENDPOINT} (chạy `make up`)")
    from cwd_server.adapters.s3_store import S3ObjectStore

    return S3ObjectStore(ENDPOINT, "cwd-documents", "cwd", "cwd-dev-secret", "us-east-1")


def test_s3_store_roundtrip(store):
    store.check()
    key = f"documents/{uuid.uuid4()}.pdf"
    body = bytes(range(256)) * 400  # ~100 KB, nhiều khối đọc
    store.put(key, io.BytesIO(body), len(body))
    try:
        assert store.size(key) == len(body)
        assert b"".join(store.get(key)) == body
        assert b"".join(store.get(key, (10, 19))) == body[10:20]
        assert key in [k for k, _ in store.list_keys("documents/")]
    finally:
        store.delete(key)
    assert key not in [k for k, _ in store.list_keys("documents/")]
    with pytest.raises(FileNotFoundError):
        store.size(key)
    with pytest.raises(FileNotFoundError):
        b"".join(store.get(key))
    store.delete(key)  # xóa lặp lại không lỗi
    with pytest.raises(ValueError):
        store.put("../x.pdf", io.BytesIO(b""), 0)


def test_s3_store_unavailable_maps_to_domain_error():
    pytest.importorskip("boto3")
    from cwd_server.adapters.s3_store import S3ObjectStore

    bad = S3ObjectStore(ENDPOINT, "khong-ton-tai-" + uuid.uuid4().hex[:8], "cwd", "cwd-dev-secret", "us-east-1")
    if not _reachable(ENDPOINT):
        pytest.skip(f"không có S3 tại {ENDPOINT}")
    with pytest.raises(StorageUnavailable):
        bad.check()
