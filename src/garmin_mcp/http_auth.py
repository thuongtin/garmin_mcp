"""HTTP bearer for Garmin MCP when the process binds off-loopback."""

from __future__ import annotations

import hmac
import os
from typing import Iterable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1", "[::1]"})
PUBLIC_PATHS = frozenset({"/healthz", "/health", "/"})


def is_loopback_bind_host(host: str) -> bool:
    return host in LOOPBACK_HOSTS


def get_http_auth_token(env: dict[str, str] | None = None) -> str | None:
    source = env if env is not None else os.environ
    value = (source.get("GARMIN_MCP_HTTP_TOKEN") or "").strip()
    return value or None


def assert_http_bind_allowed(host: str, token: str | None) -> None:
    if not is_loopback_bind_host(host) and not token:
        raise ValueError(
            "GARMIN_MCP_HTTP_TOKEN is required when GARMIN_MCP_HOST is not loopback. "
            "Refusing to expose /mcp without a bearer token."
        )


def authorize_bearer(header: str | None, token: str | None) -> bool:
    if not token:
        return True
    expected = f"Bearer {token}".encode("utf-8")
    actual = (header or "").encode("utf-8")
    if len(actual) != len(expected):
        return False
    return hmac.compare_digest(actual, expected)


class BearerTokenMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, token: str, public_paths: Iterable[str] = PUBLIC_PATHS):
        super().__init__(app)
        self.token = token
        self.public_paths = frozenset(public_paths)

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.public_paths:
            return await call_next(request)
        if authorize_bearer(request.headers.get("authorization"), self.token):
            return await call_next(request)
        return JSONResponse(
            {"error": "unauthorized"},
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        )


def attach_bearer_middleware(fastmcp, token: str) -> None:
    """Wrap FastMCP HTTP/SSE apps with a static bearer check."""
    original_http = fastmcp.streamable_http_app
    original_sse = fastmcp.sse_app

    def _wrap(app):
        app.add_middleware(BearerTokenMiddleware, token=token)
        return app

    fastmcp.streamable_http_app = lambda: _wrap(original_http())
    fastmcp.sse_app = lambda mount_path=None: _wrap(original_sse(mount_path))
