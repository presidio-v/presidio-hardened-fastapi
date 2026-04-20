# Presidio-Hardened FastAPI — Requirements

## Overview

`presidio-hardened-fastapi` is a near drop-in replacement for FastAPI that
applies production-grade security defaults through a single import swap
(`from presidio_fastapi import FastAPI`). Developed on customer
specification; also used as courseware in **PRES-EDU-SEC-101 Experiment 2**
(JWT / Auth Hardening) and **PRES-EDU-CLOUD-SOL Experiment 2** (Secure ML
Model Serving).

## Mandatory Presidio Security Extensions

- Locked-down CORS — no origins allowed unless the application configures
  them explicitly (reversal of FastAPI's permissive default)
- Rate limiting per IP (60 req/min default, exponential backoff,
  configurable)
- Security response headers — CSP, HSTS, X-Frame-Options,
  X-Content-Type-Options, Referrer-Policy, Permissions-Policy — on every
  response
- Secret redaction — automatic scan for API keys, tokens, and JWTs in
  request payloads and in log output
- OWASP input validation on top of Pydantic — SQL-injection, XSS, and path-
  traversal checks applied before handler dispatch
- On-startup CVE quick-check for FastAPI, Starlette, Pydantic, and the
  caller's security-relevant dependencies
- Structured security event logging for every hardened route
  (`presidio_fastapi` logger)
- Full GitHub security files: `SECURITY.md`, `.github/dependabot.yml`,
  `.github/workflows/codeql.yml`, `.github/workflows/ci.yml`

## Technical Requirements

- Python 3.10+
- `fastapi`, `starlette`, `pydantic` (upstream dependencies — not wrapped)
- `src/presidio_fastapi/` layout
- pytest with ≥ 90 % line coverage (enforced by `--cov-fail-under=90`)
- ruff lint + format enforced in CI
- MIT License, version 0.1.0

## Out of scope

- Authentication backends / identity providers — the library hardens
  request handling, not session issuance
- Vulnerabilities in upstream FastAPI / Starlette / Pydantic (reported
  directly to those projects)

## Version Deliberation Log

### v0.1.0 — Initial release

**Scope decision:** Import-swap pattern (`from presidio_fastapi import
FastAPI`) over a middleware-composition pattern. The customer's brief
required *zero code changes* beyond the import line so that the hardening
baseline could be rolled out across an inventory of services without per-
service review. A middleware approach would have required every service to
audit its middleware stack order.

**Scope decision:** CORS default is *deny all* rather than *warn*. The
customer's audit finding that triggered the engagement was a FastAPI
service running in production with `allow_origins=["*"]`; matching the
upstream default even with a warning was judged to preserve the failure
mode.

**Scope decision:** Rate-limit defaults (60 req/min per IP with exponential
backoff) match the customer's existing WAF policy so that the hardened
library does not introduce a second, conflicting throttle.

**Scope decision:** CVE quick-check runs at import time, not per request.
Import-time cost is amortised over process lifetime; per-request checks
would add latency to the hot path.

## SDLC

These requirements are delivered under the family-wide Presidio SDLC:
<https://github.com/presidio-v/presidio-hardened-docs/blob/main/sdlc/sdlc-report.md>.
