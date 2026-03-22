"""Tests for security headers middleware."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from presidio_fastapi import FastAPI


@pytest.mark.asyncio
async def test_default_security_headers(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200

    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["x-frame-options"] == "DENY"
    assert resp.headers["x-xss-protection"] == "1; mode=block"
    assert resp.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert "max-age=" in resp.headers["strict-transport-security"]
    assert "default-src" in resp.headers["content-security-policy"]
    assert resp.headers["cache-control"] == "no-store"


@pytest.mark.asyncio
async def test_custom_security_headers() -> None:
    app = FastAPI(
        security_headers={"X-Custom-Header": "custom-value"},
        enable_dep_check=False,
    )

    @app.get("/ping")
    async def ping():
        return {"pong": True}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/ping")

    assert resp.headers["x-custom-header"] == "custom-value"
    assert resp.headers["x-frame-options"] == "DENY"
