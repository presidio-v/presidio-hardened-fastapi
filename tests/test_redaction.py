"""Tests for secret redaction engine."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from presidio_fastapi.redaction import REDACTED, redact_dict, redact_string, redact_value


class TestRedactString:
    def test_jwt_redacted(self) -> None:
        jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123XYZ_signature"
        assert REDACTED in redact_string(jwt)

    def test_bearer_token_redacted(self) -> None:
        val = "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123XYZ_signature"
        assert REDACTED in redact_string(val)

    def test_aws_key_redacted(self) -> None:
        assert REDACTED in redact_string("AKIAIOSFODNN7EXAMPLE")

    def test_github_token_redacted(self) -> None:
        assert REDACTED in redact_string("ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklm")

    def test_stripe_key_redacted(self) -> None:
        assert REDACTED in redact_string("sk-live-abcdefghijklmnopqrstuvwx")

    def test_plain_text_unchanged(self) -> None:
        assert redact_string("hello world") == "hello world"


class TestRedactDict:
    def test_sensitive_keys_redacted(self) -> None:
        result = redact_dict({"api_key": "my-secret-key-value", "name": "alice"})
        assert result["api_key"] == REDACTED
        assert result["name"] == "alice"

    def test_password_key_redacted(self) -> None:
        result = redact_dict({"password": "hunter2", "user": "bob"})
        assert result["password"] == REDACTED
        assert result["user"] == "bob"

    def test_token_key_redacted(self) -> None:
        result = redact_dict({"access_token": "abc123", "user_id": 42})
        assert result["access_token"] == REDACTED
        assert result["user_id"] == 42

    def test_nested_redaction(self) -> None:
        data = {"config": {"password": "secret123"}}
        result = redact_value(data)
        assert result["config"]["password"] == REDACTED


class TestRedactEndpoint:
    @pytest.mark.asyncio
    async def test_secret_endpoint_redacts_api_key(self, client: AsyncClient) -> None:
        resp = await client.get("/secret")
        assert resp.status_code == 200
        body = resp.json()
        assert body["api_key"] == REDACTED
        assert body["user"] == "alice"

    @pytest.mark.asyncio
    async def test_echo_redacts_sensitive_keys(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/echo",
            json={"password": "supersecret", "message": "hi"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["password"] == REDACTED
        assert body["message"] == "hi"
