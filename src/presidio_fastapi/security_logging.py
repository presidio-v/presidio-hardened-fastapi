"""Security event logging — structured log entries for the hardening layer.

v0.2.0: Includes sink-level RedactingFilter for the presidio_fastapi logger
to enforce secret redaction on all log records (family best practice).
"""

from __future__ import annotations

import logging
import re
from typing import Any

from presidio_fastapi.redaction import redact_string  # reuse existing patterns where possible

logger = logging.getLogger("presidio_fastapi.security")

_LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s — %(message)s"


# Minimal patterns for the filter (complements the existing redact_* helpers)
_FASTAPI_SECRET_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(sk_(?:live|test)_)[A-Za-z0-9]+"), r"\1***REDACTED***"),
    (re.compile(r"(sk-ant-)[A-Za-z0-9\-_]+"), r"\1***REDACTED***"),
    (re.compile(r"(Bearer\s+)[A-Za-z0-9\-._~+/]+=*"), r"\1***REDACTED***"),
    (re.compile(r"(access_token=)[^&\s]+"), r"\1***REDACTED***"),
    (re.compile(r"(api_key=)[^&\s]+"), r"\1***REDACTED***"),
    (re.compile(r"(Authorization:\s*)[^\r\n]+", re.IGNORECASE), r"\1***REDACTED***"),
]


class RedactingFilter(logging.Filter):
    """Sink-level filter that redacts secrets from every log record."""

    def __init__(self) -> None:
        super().__init__()

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:  # pragma: no cover
            return True
        for pattern, repl in _FASTAPI_SECRET_PATTERNS:
            message = pattern.sub(repl, message)
        # Also run the existing string redactor for broader coverage
        record.msg = redact_string(message)
        record.args = None
        return True


def install_log_redaction() -> RedactingFilter:
    """Install RedactingFilter on the presidio_fastapi root logger (idempotent)."""
    root = logging.getLogger("presidio_fastapi")
    for f in root.filters:
        if isinstance(f, RedactingFilter):
            return f
    flt = RedactingFilter()
    root.addFilter(flt)
    return flt


def setup_logging(level: int = logging.INFO) -> None:
    """Configure the presidio_fastapi logger hierarchy. Installs sink redaction (v0.2)."""
    root = logging.getLogger("presidio_fastapi")
    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        root.addHandler(handler)
    root.setLevel(level)
    install_log_redaction()


def log_security_event(event: str, *, extra: dict[str, Any] | None = None) -> None:
    """Emit a structured security-event log line."""
    msg = f"[SECURITY] {event}"
    if extra:
        msg += f" | {extra}"
    logger.info(msg)
