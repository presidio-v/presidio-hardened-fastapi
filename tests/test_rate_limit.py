"""Tests for rate limiting functionality."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from presidio_fastapi import FastAPI, Request
from presidio_fastapi.rate_limit import limiter


@pytest.mark.asyncio
async def test_rate_limit_returns_429() -> None:
    app = FastAPI(enable_rate_limiting=True, enable_dep_check=False)

    @app.get("/limited")
    @limiter.limit("2/minute")
    async def limited(request: Request):
        return {"ok": True}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        r1 = await ac.get("/limited")
        assert r1.status_code == 200

        r2 = await ac.get("/limited")
        assert r2.status_code == 200

        r3 = await ac.get("/limited")
        assert r3.status_code == 429
        body = r3.json()
        assert "Rate limit" in body["detail"]
        assert "Retry-After" in r3.headers


@pytest.mark.asyncio
async def test_rate_limit_disabled() -> None:
    app = FastAPI(enable_rate_limiting=False, enable_dep_check=False)

    @app.get("/unlimited")
    async def unlimited():
        return {"ok": True}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        for _ in range(10):
            resp = await ac.get("/unlimited")
            assert resp.status_code == 200
