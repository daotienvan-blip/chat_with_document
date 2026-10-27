"""Kiểm tra phản hồi theo docs/04-design/openapi.yaml (S1-03; dùng lại ở bộ hợp đồng S8-03)."""
from __future__ import annotations

import functools
import re

import jsonschema
import yaml

from cwd_server.platform.config import REPO_DIR

SPEC_PATH = REPO_DIR / "docs" / "04-design" / "openapi.yaml"


@functools.cache
def spec() -> dict:
    return yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))


def _conv(s):
    if isinstance(s, dict):
        s = dict(s)
        if s.pop("nullable", False):
            if "type" in s:
                s["type"] = [s["type"], "null"]
            if "enum" in s and None not in s["enum"]:
                s["enum"] = s["enum"] + [None]
        if "$ref" in s:
            s["$ref"] = s["$ref"].replace("#/components/schemas/", "#/definitions/")
        s.pop("example", None)
        return {k: _conv(v) for k, v in s.items()}
    if isinstance(s, list):
        return [_conv(x) for x in s]
    return s


@functools.cache
def _definitions() -> dict:
    return {k: _conv(v) for k, v in spec()["components"]["schemas"].items()}


def _resolve(obj):
    if isinstance(obj, dict) and "$ref" in obj:
        node = spec()
        for part in obj["$ref"].lstrip("#/").split("/"):
            node = node[part]
        return node
    return obj


def operation(path: str, method: str) -> dict:
    return spec()["paths"][path][method.lower()]


def template_for(url_path: str) -> str:
    p = url_path.split("?")[0]
    if p.startswith("/api/v1"):
        p = p[len("/api/v1"):]
    for tmpl in spec()["paths"]:
        rx = "^" + re.sub(r"\{[^}]+\}", "[^/]+", tmpl) + "$"
        if re.match(rx, p):
            return tmpl
    raise AssertionError(f"đường dẫn không có trong openapi.yaml: {url_path}")


def assert_matches_openapi(resp, method: str | None = None) -> None:
    method = method or resp.request.method
    tmpl = template_for(str(resp.request.url.path))
    op = operation(tmpl, method)
    code = str(resp.status_code)
    assert code in op["responses"], f"{method} {tmpl}: mã {code} không khai báo trong openapi.yaml"
    r = _resolve(op["responses"][code])
    content = r.get("content") or {}
    ctype = resp.headers.get("content-type", "").split(";")[0]
    if not content:
        assert not resp.content, f"{method} {tmpl} {code}: không được có thân"
        return
    assert ctype in content, f"{method} {tmpl} {code}: content-type {ctype} không khai báo ({list(content)})"
    schema = content[ctype].get("schema", {})
    if ctype.endswith("json"):
        full = {**_conv(schema), "definitions": _definitions()}
        jsonschema.validate(resp.json(), full)
    for h in (r.get("headers") or {}):
        if h in ("X-Request-Id", "Location"):
            assert h.lower() in {k.lower() for k in resp.headers}, f"thiếu header {h}"
