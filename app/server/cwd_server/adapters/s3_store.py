"""ObjectStorePort trên S3 (S0-06). Cần extra `s3` (boto3).

Kiểm thử tích hợp: tests/integration/test_s3_store.py trên SeaweedFS của `make up`; bản demo dùng LocalFsObjectStore.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import BinaryIO

from cwd_server.adapters.stores import check_key
from cwd_server.core.errors import StorageUnavailable


class S3ObjectStore:
    def __init__(self, endpoint: str | None, bucket: str, access_key: str | None, secret_key: str | None,
                 region: str | None):
        import boto3
        from botocore.config import Config

        self.bucket = bucket
        self.s3 = boto3.client("s3", endpoint_url=endpoint, aws_access_key_id=access_key,
                               aws_secret_access_key=secret_key, region_name=region,
                               config=Config(retries={"max_attempts": 3, "mode": "standard"}))
        from botocore.exceptions import BotoCoreError, ClientError
        self._errors = (BotoCoreError, ClientError)

    def _wrap(self, fn, *a, **kw):
        try:
            return fn(*a, **kw)
        except self._errors as e:
            code = getattr(e, "response", {}).get("Error", {}).get("Code")
            if code in ("NoSuchKey", "404"):
                raise FileNotFoundError() from e
            raise StorageUnavailable() from e

    def put(self, key: str, stream: BinaryIO, size: int) -> None:
        self._wrap(self.s3.upload_fileobj, stream, self.bucket, check_key(key),
                   ExtraArgs={"ContentType": "application/pdf"})

    def size(self, key: str) -> int:
        return self._wrap(self.s3.head_object, Bucket=self.bucket, Key=check_key(key))["ContentLength"]

    def get(self, key: str, byte_range: tuple[int, int] | None = None) -> Iterator[bytes]:
        kw = {"Range": f"bytes={byte_range[0]}-{byte_range[1]}"} if byte_range else {}
        body = self._wrap(self.s3.get_object, Bucket=self.bucket, Key=check_key(key), **kw)["Body"]
        return iter(lambda: body.read(64 * 1024), b"")

    def delete(self, key: str) -> None:
        self._wrap(self.s3.delete_object, Bucket=self.bucket, Key=check_key(key))

    def list_keys(self, prefix: str) -> Iterator[tuple[str, float]]:
        pages = self._wrap(self.s3.get_paginator("list_objects_v2").paginate, Bucket=self.bucket, Prefix=prefix)
        for page in pages:
            for o in page.get("Contents", []):
                yield o["Key"], o["LastModified"].timestamp()

    def check(self) -> None:
        try:
            self._wrap(self.s3.head_bucket, Bucket=self.bucket)
        except FileNotFoundError as e:  # bucket thiếu = lỗi hạ tầng, không phải thiếu tệp
            raise StorageUnavailable() from e
