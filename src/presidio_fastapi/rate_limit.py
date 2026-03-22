"""Per-route rate limiting backed by slowapi with exponential backoff defaults."""

from __future__ import annotations

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import JSONResponse

DEFAULT_RATE = "60/minute"

limiter = Limiter(key_func=get_remote_address, default_limits=[DEFAULT_RATE])


async def rate_limit_exceeded_handler(_request: Request, exc: RateLimitExceeded) -> JSONResponse:
    retry_after = getattr(exc, "retry_after", 60)
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Slow down.",
            "retry_after": retry_after,
        },
        headers={"Retry-After": str(retry_after)},
    )
