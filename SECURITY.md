# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |

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

## Software Development Lifecycle

This repository is developed under the Presidio hardened-family SDLC. The public report
— scope, standards mapping, threat-model gates, and supply-chain controls — is at
<https://github.com/presidio-v/presidio-hardened-docs/blob/main/sdlc/sdlc-report.md>.
