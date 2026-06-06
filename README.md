# presidio-hardened-fastapi

A hardened, near drop-in replacement for FastAPI with strong security defaults.

> **Version 0.2.0** — MIT License (v0.2 adds sink redaction, pip-audit in CI/dev, doc alignment)

## Quick Start

```bash
pip install presidio-hardened-fastapi
```

```python
# Just swap the import — your existing FastAPI code gains security defaults.
from presidio_fastapi import FastAPI, APIRouter

app = FastAPI(title="My Secure API")

@app.get("/")
async def root():
    return {"status": "hardened"}
```

## v0.2.0 Changes
- Sink-level secret redaction via RedactingFilter (automatic for the logger).
- pip-audit integrated in dev extras and CI.
- Docs updated for accuracy (redaction/validation are strong helpers; use them explicitly on input).
- Version and dependency improvements.

## What You Get (Automatically)

| Security Feature | Plain FastAPI | presidio-hardened-fastapi |
|---|---|---|
| **CORS** | Wide open by default | Locked down — no origins allowed unless configured |
| **Rate Limiting** | None | 60 req/min per IP with exponential backoff (configurable) |
| **Security Headers** | None | CSP, HSTS, X-Frame-Options, X-Content-Type-Options, etc. |
| **Secret Redaction** | None | Helpers + automatic sink-level RedactingFilter on presidio_fastapi logs (v0.2) |
| **OWASP Validation** | Pydantic only | SQL injection, XSS, path traversal checks (opt-in helper: call check_owasp()) |
| **Dependency Check** | None | On-startup + pip-audit in [dev]/CI (v0.2) |
| **Security Logging** | None | Structured security event logs (with sink redaction) |

## Side-by-Side Comparison

### Plain FastAPI

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# You must manually add CORS...
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dangerous!
    allow_methods=["*"],
    allow_headers=["*"],
)

# No rate limiting
# No security headers
# No input validation beyond Pydantic
# No secret redaction

@app.post("/login")
async def login(data: dict):
    return {"token": "sk-live-abc123secret"}  # leaked!
```

### presidio-hardened-fastapi

```python
from presidio_fastapi import FastAPI, Request, check_owasp, redact_dict

app = FastAPI(
    title="My Secure API",
    cors_allow_origins=["https://myapp.com"],  # explicit allowlist
)

@app.post("/login")
async def login(request: Request):
    body = await request.json()
    check_owasp(body)  # blocks SQL injection, XSS, path traversal
    # Process login...
    response_data = {"token": "sk-live-abc123secret"}
    return redact_dict(response_data)  # token is redacted in response
```

**Automatic protections applied with zero extra code (v0.2):**
- Strict CORS (only `https://myapp.com`)
- Rate limiting (60 req/min per IP)
- Security headers (CSP, HSTS, X-Frame-Options, ...)
- Sink redaction on all presidio_fastapi logs
- Startup dependency audit (plus pip-audit available)
- Security event logging

Note: `check_owasp()` and `redact_*` are powerful helpers — call them on untrusted input/response data for full effect (validation/redaction of bodies is not fully automatic to avoid breaking existing Pydantic models).

## Configuration

```python
from presidio_fastapi import FastAPI

app = FastAPI(
    cors_allow_origins=["https://trusted.com"],
    cors_allow_methods=["GET", "POST"],
    cors_allow_headers=["Authorization"],
    cors_allow_credentials=True,
    enable_rate_limiting=True,
    enable_owasp_validation=True,
    enable_dep_check=True,
    security_headers={
        "Content-Security-Policy": "default-src 'self' https://cdn.example.com",
    },
)
```

## Per-Route Rate Limiting

```python
from presidio_fastapi import FastAPI, Request
from presidio_fastapi import limiter

app = FastAPI()

@app.get("/expensive")
@limiter.limit("5/minute")
async def expensive_endpoint(request: Request):
    return {"data": "rate-limited to 5/min"}
```

## Redaction Utilities

```python
from presidio_fastapi import redact_dict, redact_value

data = {"user": "alice", "api_key": "sk-live-xxxxxxxxxxxx"}
safe = redact_dict(data)
# {"user": "alice", "api_key": "***REDACTED***"}
```

## OWASP Input Validation

```python
from presidio_fastapi import check_owasp, HTTPException

try:
    check_owasp({"query": "'; DROP TABLE users;--"})
except HTTPException as e:
    print(e.detail)  # "Potential SQL injection detected"
```

## Development

```bash
git clone https://github.com/presidio-security/presidio-hardened-fastapi
cd presidio-hardened-fastapi
uv venv .venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run tests
pytest --cov=presidio_fastapi

# Lint & format
ruff format .
ruff check . --fix
```

## Security

See [SECURITY.md](SECURITY.md) for the security policy and vulnerability reporting instructions.

## License

MIT — see [LICENSE](LICENSE) for details.

---

## SDLC

This repository is developed under the Presidio hardened-family SDLC:
<https://github.com/presidio-v/presidio-hardened-docs/blob/main/sdlc/sdlc-report.md>.
