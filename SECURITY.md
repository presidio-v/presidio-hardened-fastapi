# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a vulnerability in `presidio-hardened-fastapi`, please report it responsibly.

### How to Report

1. **Do NOT open a public GitHub issue** for security vulnerabilities.
2. Email: **security@presidio.dev** with:
   - A description of the vulnerability
   - Steps to reproduce
   - The potential impact
   - Any suggested fixes (optional)

### What to Expect

- **Acknowledgement** within 48 hours of your report.
- **Status update** within 7 days with our assessment and expected timeline.
- **Resolution** — we aim to patch critical vulnerabilities within 14 days.
- **Credit** — reporters will be credited in the release notes (unless anonymity is requested).

### Scope

The following are in scope:

- The `presidio_fastapi` Python package and its middleware/wrappers
- Bypass of CORS, rate limiting, OWASP validation, or redaction features
- Information leakage through logging or error messages
- Dependency chain vulnerabilities

### Out of Scope

- Vulnerabilities in upstream FastAPI, Starlette, or Pydantic (please report those to their respective maintainers)
- Denial-of-service attacks against the rate limiter itself
- Issues requiring physical access to the server

## Security Features

This package provides the following security hardening on top of FastAPI:

- **Strict CORS** — locked-down defaults, explicit allowlisting required
- **Rate Limiting** — per-IP with configurable limits and exponential backoff
- **Security Headers** — CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy
- **Secret Redaction** — automatic scanning for API keys, tokens, JWTs, AWS keys
- **OWASP Validation** — SQL injection, XSS, and path traversal detection
- **Dependency Auditing** — on-startup version checks for known-vulnerable releases
- **Security Event Logging** — structured logs for all hardening actions

## Security Best Practices

When using this package:

1. Always set explicit `cors_allow_origins` — never use `["*"]`
2. Use `check_owasp()` on all user-supplied input
3. Use `redact_dict()` / `redact_value()` before logging or returning sensitive data
4. Keep dependencies updated — run `pip audit` regularly
5. Review the startup security logs for any warnings
