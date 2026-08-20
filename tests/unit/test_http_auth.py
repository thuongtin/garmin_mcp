"""Unit tests for off-loopback HTTP bearer auth."""

import pytest

from garmin_mcp.http_auth import (
    assert_http_bind_allowed,
    authorize_bearer,
    get_http_auth_token,
    is_loopback_bind_host,
)


def test_loopback_hosts():
    assert is_loopback_bind_host("127.0.0.1")
    assert is_loopback_bind_host("localhost")
    assert not is_loopback_bind_host("0.0.0.0")
    assert not is_loopback_bind_host("10.10.10.13")


def test_token_from_env():
    assert get_http_auth_token({}) is None
    assert get_http_auth_token({"GARMIN_MCP_HTTP_TOKEN": "  abc  "}) == "abc"


def test_bind_requires_token_off_loopback():
    assert_http_bind_allowed("127.0.0.1", None)
    assert_http_bind_allowed("0.0.0.0", "secret")
    with pytest.raises(ValueError, match="GARMIN_MCP_HTTP_TOKEN"):
        assert_http_bind_allowed("0.0.0.0", None)


def test_authorize_bearer():
    assert authorize_bearer(None, None) is True
    assert authorize_bearer("Bearer secret", "secret") is True
    assert authorize_bearer("Bearer other", "secret") is False
    assert authorize_bearer(None, "secret") is False
    assert authorize_bearer("secret", "secret") is False
