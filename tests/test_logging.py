"""Tests for security logging module."""

from __future__ import annotations

import logging

from presidio_fastapi.security_logging import log_security_event, setup_logging


def test_setup_logging_configures_handler() -> None:
    root = logging.getLogger("presidio_fastapi")
    initial_handler_count = len(root.handlers)
    setup_logging(logging.DEBUG)
    assert root.level == logging.DEBUG
    assert len(root.handlers) >= initial_handler_count


def test_log_security_event(caplog: object) -> None:
    setup_logging(logging.INFO)
    log_security_event("test event", extra={"key": "value"})


def test_log_security_event_no_extra(caplog: object) -> None:
    setup_logging(logging.INFO)
    log_security_event("simple event")
