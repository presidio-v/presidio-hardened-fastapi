"""On-startup dependency / CVE quick-check for FastAPI and common deps."""

from __future__ import annotations

import importlib.metadata
import logging
import sys
from typing import Any

logger = logging.getLogger("presidio_fastapi.dep_check")

CHECKED_PACKAGES = ["fastapi", "starlette", "uvicorn", "pydantic", "httpx"]

MIN_VERSIONS: dict[str, str] = {
    "fastapi": "0.100.0",
    "starlette": "0.27.0",
    "pydantic": "2.0.0",
}


def _parse_version(v: str) -> tuple[int, ...]:
    parts: list[int] = []
    for segment in v.split(".")[:3]:
        digits = ""
        for ch in segment:
            if ch.isdigit():
                digits += ch
            else:
                break
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def _version_lt(a: str, b: str) -> bool:
    return _parse_version(a) < _parse_version(b)


def check_dependencies() -> list[dict[str, Any]]:
    """Return a list of warnings about installed dependency versions."""
    warnings: list[dict[str, Any]] = []

    for pkg in CHECKED_PACKAGES:
        try:
            version = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            continue

        info: dict[str, Any] = {"package": pkg, "installed": version}

        if pkg in MIN_VERSIONS and _version_lt(version, MIN_VERSIONS[pkg]):
            info["warning"] = f"{pkg}=={version} is below recommended minimum {MIN_VERSIONS[pkg]}"
            warnings.append(info)
            logger.warning("Presidio dep-check: %s", info["warning"])

    return warnings


def log_dependency_report() -> None:
    """Log a summary of dependency versions at startup."""
    logger.info("Presidio dependency check — Python %s", sys.version.split()[0])
    warnings = check_dependencies()
    if warnings:
        for w in warnings:
            logger.warning("  ⚠ %s", w["warning"])
    else:
        logger.info("  All checked dependencies look OK.")
