"""Shared fixtures for presidio_fastapi tests."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from presidio_fastapi import FastAPI, Request, check_owasp, redact_dict


def _build_app() -> FastAPI:
    app = FastAPI(
        title="Test App",
        cors_allow_origins=["https://trusted.example.com"],
        cors_allow_methods=["GET", "POST"],
        cors_allow_headers=["Authorization"],
        enable_rate_limiting=True,
        enable_dep_check=False,
    )

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/echo")
    async def echo(request: Request):
        body = await request.json()
        check_owasp(body)
        return redact_dict(body)

    @app.get("/secret")
    async def secret():
        return redact_dict({"api_key": "sk-live-test1234567890", "user": "alice"})

    return app


@pytest.fixture()
def app() -> FastAPI:
    return _build_app()


@pytest.fixture()
async def client(app: FastAPI) -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
