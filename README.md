# presidio-hardened-fastapi

A hardened, near drop-in replacement for FastAPI with strong security defaults.

> **Version 0.1.0** — MIT License

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

## What You Get (Automatically)

| Security Feature | Plain FastAPI | presidio-hardened-fastapi |
|---|---|---|
| **CORS** | Wide open by default | Locked down — no origins allowed unless configured |
| **Rate Limiting** | None | 60 req/min per IP with exponential backoff (configurable) |
| **Security Headers** | None | CSP, HSTS, X-Frame-Options, X-Content-Type-Options, etc. |
| **Secret Redaction** | None | Auto-scans for API keys, tokens, JWTs in request data |
| **OWASP Validation** | Pydantic only | SQL injection, XSS, path traversal checks on top of Pydantic |
| **Dependency Check** | None | On-startup CVE/version check for FastAPI and common deps |
| **Security Logging** | None | Structured security event logs for every hardened route |

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

**Automatic protections applied with zero extra code:**
- Strict CORS (only `https://myapp.com`)
- Rate limiting (60 req/min per IP)
- Security headers (CSP, HSTS, X-Frame-Options, ...)
- Startup dependency audit
- Security event logging

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
