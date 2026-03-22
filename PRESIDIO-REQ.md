# Presidio-Hardened FastAPI – Top-Level Requirements

## Overview
Build a production-ready Python package `presidio-hardened-fastapi` that acts as a hardened, near drop-in replacement for FastAPI.
Users write: `from presidio_fastapi import FastAPI, APIRouter` (and similar) instead of `from fastapi import ...`, and their existing FastAPI code mostly works unchanged while gaining strong security defaults.

## Mandatory Presidio Security Extensions
- Automatic strict CORS policy (configurable but defaults to most restrictive)
- Built-in per-route rate limiting with exponential backoff (using slowapi or similar)
- Request data secret redaction: scan JSON bodies, query params, headers for tokens/keys and redact in logs/responses
- Automatic input validation hardening (extra OWASP rules on top of Pydantic)
- Security headers middleware (CSP, X-Frame-Options, HSTS hints, etc.)
- On-startup CVE/dependency quick-check for FastAPI and common deps
- Security event logging ("Presidio hardening layer applied to route X")
- Full GitHub security files: SECURITY.md, .github/dependabot.yml, .github/workflows/codeql.yml + pytest + ruff workflow

## Technical Requirements
- Python 3.9+
- Modern pyproject.toml + hatchling/uv
- src/presidio_fastapi/__init__.py layout with re-exports and middleware injection
- Do NOT copy FastAPI source; wrap/extend via middleware, routers, and dependency overrides
- 90%+ test coverage with pytest + httpx for API testing
- Black + ruff enforced
- README.md with side-by-side examples: plain FastAPI vs presidio-hardened-fastapi showing security improvements
- LICENSE = MIT
- Version = 0.1.0

Deliver the complete working project ready for GitHub publish.