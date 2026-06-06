"""Security headers middleware — CSP, HSTS, X-Frame-Options, etc."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

DEFAULT_SECURITY_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), camera=(), microphone=()",
    "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'",
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
    "Cache-Control": "no-store",
    "Pragma": "no-cache",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Injects configurable security headers into every response."""

    def __init__(self, app: object, headers: dict[str, str] | None = None) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self.headers = {**DEFAULT_SECURITY_HEADERS, **(headers or {})}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        for name, value in self.headers.items():
            response.headers[name] = value
        return response
