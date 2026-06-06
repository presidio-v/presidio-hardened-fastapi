"""presidio-hardened-fastapi — a hardened drop-in replacement for FastAPI."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator, Sequence
from contextlib import asynccontextmanager
from typing import Any

import fastapi
from fastapi import (
    APIRouter,  # noqa: F401 — re-export
    BackgroundTasks,  # noqa: F401
    Depends,  # noqa: F401
    File,  # noqa: F401
    Form,  # noqa: F401
    Header,  # noqa: F401
    HTTPException,  # noqa: F401
    Path,  # noqa: F401
    Query,  # noqa: F401
    Request,  # noqa: F401
    Response,  # noqa: F401
    UploadFile,  # noqa: F401
    status,  # noqa: F401
)
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler as _slowapi_default_handler  # noqa: F401
from slowapi.errors import RateLimitExceeded

from presidio_fastapi.dep_check import log_dependency_report
from presidio_fastapi.headers import SecurityHeadersMiddleware
from presidio_fastapi.rate_limit import limiter, rate_limit_exceeded_handler
from presidio_fastapi.redaction import redact_dict, redact_value  # noqa: F401
from presidio_fastapi.security_logging import (
    RedactingFilter,
    install_log_redaction,
    log_security_event,
    setup_logging,
)
from presidio_fastapi.validation import check_owasp  # noqa: F401

__version__ = "0.2.0"
__all__ = [
    "FastAPI",
    "APIRouter",
    "HardenedFastAPI",
    "limiter",
    "redact_dict",
    "redact_value",
    "check_owasp",
    "RedactingFilter",
    "install_log_redaction",
    "__version__",
]

_logger = logging.getLogger("presidio_fastapi")


def _build_lifespan(
    enable_dep_check: bool,
    user_lifespan: Any | None,
) -> Any:
    """Create a lifespan context manager that runs Presidio startup tasks."""

    @asynccontextmanager
    async def _lifespan(app: fastapi.FastAPI) -> AsyncGenerator[None, None]:
        if enable_dep_check:
            log_dependency_report()

        for route in app.routes:
            path = getattr(route, "path", None)
            if path:
                log_security_event(f"Presidio hardening layer applied to route {path}")

        if user_lifespan is not None:
            async with user_lifespan(app):
                yield
        else:
            yield

    return _lifespan


class HardenedFastAPI(fastapi.FastAPI):
    """FastAPI subclass that applies Presidio security defaults on construction."""

    def __init__(
        self,
        *,
        cors_allow_origins: Sequence[str] = (),
        cors_allow_methods: Sequence[str] = ("GET",),
        cors_allow_headers: Sequence[str] = (),
        cors_allow_credentials: bool = False,
        security_headers: dict[str, str] | None = None,
        enable_rate_limiting: bool = True,
        enable_owasp_validation: bool = True,
        enable_dep_check: bool = True,
        log_level: int = logging.INFO,
        **kwargs: Any,
    ) -> None:
        setup_logging(log_level)

        user_lifespan = kwargs.pop("lifespan", None)
        kwargs["lifespan"] = _build_lifespan(enable_dep_check, user_lifespan)

        super().__init__(**kwargs)

        self.add_middleware(
            CORSMiddleware,
            allow_origins=list(cors_allow_origins),
            allow_methods=list(cors_allow_methods),
            allow_headers=list(cors_allow_headers),
            allow_credentials=cors_allow_credentials,
        )
        log_security_event(
            "Strict CORS policy applied", extra={"origins": list(cors_allow_origins)}
        )

        self.add_middleware(SecurityHeadersMiddleware, headers=security_headers)
        log_security_event("Security headers middleware applied")

        if enable_rate_limiting:
            self.state.limiter = limiter
            self.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)  # type: ignore[arg-type]
            log_security_event("Rate limiting enabled", extra={"default": "60/minute"})

        self._enable_owasp = enable_owasp_validation


# Alias so `from presidio_fastapi import FastAPI` works as a drop-in.
FastAPI = HardenedFastAPI
