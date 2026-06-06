# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.2.x   | :white_check_mark: (current) |
| 0.1.x   | :white_check_mark: (legacy) |

## Reporting a Vulnerability

Please report security vulnerabilities by opening a private GitHub Security Advisory
(via the "Security" tab → "Report a vulnerability") rather than a public issue.

Include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

You will receive an acknowledgement within 5 business days. We aim to release a patch
within 30 days of a confirmed vulnerability.

## Security Features (v0.2.0)

This package provides the following security hardening on top of FastAPI:

- **Strict CORS** — locked-down defaults, explicit allowlisting required
- **Rate Limiting** — per-IP with configurable limits and exponential backoff
- **Security Headers** — CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy
- **Secret Redaction** — helpers (redact_dict/value) + sink-level RedactingFilter on the presidio_fastapi logger for all log records (v0.2 addition)
- **OWASP Validation** — SQL injection, XSS, and path traversal detection helpers (use check_owasp() on untrusted input; see best practices)
- **Dependency Auditing** — on-startup version checks + pip-audit in dev/CI (v0.2)
- **Security Event Logging** — structured logs for all hardening actions (with sink redaction)

## Security Best Practices

When using this package:

1. Always set explicit `cors_allow_origins` — never use `["*"]`
2. Use `check_owasp()` on all user-supplied input (validation is opt-in helper)
3. Use `redact_dict()` / `redact_value()` before logging/returning sensitive data; sink redaction is automatic for presidio_fastapi logs (v0.2)
4. Keep dependencies updated — `pip-audit` is in [dev] and CI
5. Review the startup security logs for any warnings
6. The RedactingFilter and other primitives are installed automatically on HardenedFastAPI use.

## Software Development Lifecycle

This repository is developed under the Presidio hardened-family SDLC. The public report
— scope, standards mapping, threat-model gates, and supply-chain controls — is at
<https://github.com/presidio-v/presidio-hardened-docs/blob/main/sdlc/sdlc-report.md>.
