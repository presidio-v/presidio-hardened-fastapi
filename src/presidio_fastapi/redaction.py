"""Secret redaction engine — scans strings, dicts and query params for sensitive tokens."""

from __future__ import annotations

import re
from typing import Any

_SECRET_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"""(?ix)
        (?:api[_-]?key|secret|token|password|passwd|authorization|bearer|access[_-]?token
        |client[_-]?secret|private[_-]?key|api[_-]?secret|auth[_-]?token|session[_-]?id
        |credit[_-]?card|ssn|social[_-]?security)
        \s*[=:]\s*
        ["']?([A-Za-z0-9\-_./+=]{8,})["']?
        """
    ),
    re.compile(r"\b(?:sk|pk)[-_](?:live|test)[-_][A-Za-z0-9]{20,}\b"),
    re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9\-_./+=]{20,}\b", re.IGNORECASE),
]

REDACTED = "***REDACTED***"

SENSITIVE_KEY_FRAGMENTS = frozenset(
    {
        "token",
        "secret",
        "password",
        "passwd",
        "api_key",
        "apikey",
        "api-key",
        "authorization",
        "private_key",
        "access_token",
        "client_secret",
        "session_id",
        "credit_card",
        "ssn",
    }
)


def _key_looks_sensitive(key: str) -> bool:
    lowered = key.lower().replace("-", "_")
    return any(frag in lowered for frag in SENSITIVE_KEY_FRAGMENTS)


def redact_string(value: str) -> str:
    """Replace any detected secrets in *value* with the REDACTED sentinel."""
    result = value
    for pattern in _SECRET_PATTERNS:
        result = pattern.sub(REDACTED, result)
    return result


def redact_value(value: Any) -> Any:
    """Recursively redact secrets from dicts, lists, or plain strings."""
    if isinstance(value, dict):
        return redact_dict(value)
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, str):
        return redact_string(value)
    return value


def redact_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Redact values whose *keys* look sensitive, plus pattern-scan all string values."""
    out: dict[str, Any] = {}
    for k, v in data.items():
        if _key_looks_sensitive(k) and isinstance(v, str) and len(v) > 0:
            out[k] = REDACTED
        else:
            out[k] = redact_value(v)
    return out
