"""Tests for lifespan integration (dep check + route logging on startup)."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import pytest

from presidio_fastapi import FastAPI, _build_lifespan


@pytest.mark.asyncio
async def test_lifespan_runs_dep_check(caplog: object) -> None:
    app = FastAPI(enable_dep_check=True)

    @app.get("/ping")
    async def ping():
        return "pong"

    lifespan = _build_lifespan(enable_dep_check=True, user_lifespan=None)
    async with lifespan(app):
        pass


@pytest.mark.asyncio
async def test_lifespan_wraps_user_lifespan() -> None:
    startup_ran = False

    @asynccontextmanager
    async def user_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        nonlocal startup_ran
        startup_ran = True
        yield

    app = FastAPI(lifespan=user_lifespan, enable_dep_check=False)

    built_lifespan = _build_lifespan(enable_dep_check=False, user_lifespan=user_lifespan)
    async with built_lifespan(app):
        pass

    assert startup_ran is True


@pytest.mark.asyncio
async def test_lifespan_without_user_lifespan() -> None:
    app = FastAPI(enable_dep_check=False)

    @app.get("/test")
    async def test_endpoint():
        return {"ok": True}

    lifespan = _build_lifespan(enable_dep_check=False, user_lifespan=None)
    async with lifespan(app):
        pass
