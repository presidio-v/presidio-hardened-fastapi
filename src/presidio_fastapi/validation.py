"""OWASP-inspired input validation hardening on top of Pydantic."""

from __future__ import annotations

import re
from typing import Any

from fastapi import HTTPException

_SQL_INJECTION_PATTERN = re.compile(
    r"""(?ix)
    (?:--|;|\b(?:union\s+select|drop\s+table|insert\s+into|delete\s+from
    |update\s+\w+\s+set|exec\s*\(|execute\s|xp_|sp_))
    """,
)

_XSS_PATTERN = re.compile(
    r"""(?i)<\s*(?:script|img|svg|iframe|object|embed|link|style|meta|body|form)\b""",
)

_PATH_TRAVERSAL_PATTERN = re.compile(r"\.\.[/\\]")

_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (_SQL_INJECTION_PATTERN, "Potential SQL injection detected"),
    (_XSS_PATTERN, "Potential XSS payload detected"),
    (_PATH_TRAVERSAL_PATTERN, "Path traversal attempt detected"),
]


def check_owasp(value: Any) -> None:
    """Raise 400 if *value* (recursively) contains a suspicious pattern."""
    if isinstance(value, str):
        for pattern, message in _PATTERNS:
            if pattern.search(value):
                raise HTTPException(status_code=400, detail=message)
    elif isinstance(value, dict):
        for v in value.values():
            check_owasp(v)
    elif isinstance(value, list):
        for item in value:
            check_owasp(item)
