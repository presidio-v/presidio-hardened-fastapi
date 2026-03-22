"""Tests for CORS policy."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cors_allows_trusted_origin(client: AsyncClient) -> None:
    resp = await client.options(
        "/health",
        headers={
            "Origin": "https://trusted.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.headers.get("access-control-allow-origin") == "https://trusted.example.com"


@pytest.mark.asyncio
async def test_cors_blocks_untrusted_origin(client: AsyncClient) -> None:
    resp = await client.options(
        "/health",
        headers={
            "Origin": "https://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.headers.get("access-control-allow-origin") is None
