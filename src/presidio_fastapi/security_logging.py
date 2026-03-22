"""Security event logging — structured log entries for the hardening layer."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("presidio_fastapi.security")

_LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s — %(message)s"


def setup_logging(level: int = logging.INFO) -> None:
    """Configure the presidio_fastapi logger hierarchy."""
    root = logging.getLogger("presidio_fastapi")
    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        root.addHandler(handler)
    root.setLevel(level)


def log_security_event(event: str, *, extra: dict[str, Any] | None = None) -> None:
    """Emit a structured security-event log line."""
    msg = f"[SECURITY] {event}"
    if extra:
        msg += f" | {extra}"
    logger.info(msg)
