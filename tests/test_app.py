"""Integration tests for the HardenedFastAPI app class."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from presidio_fastapi import FastAPI, HardenedFastAPI, __version__


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_hardened_is_fastapi_subclass() -> None:
    assert issubclass(HardenedFastAPI, FastAPI)


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_minimal_app_boots() -> None:
    app = FastAPI(enable_dep_check=False)

    @app.get("/ping")
    async def ping():
        return "pong"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/ping")
    assert resp.status_code == 200
