"""Experiment 2 runner: start vulnerable or hardened FastAPI server.

Usage:
    python main.py --mode vulnerable --port 8000
    python main.py --mode hardened  --port 8001
"""

# ruff: noqa: T201, N806, B904, B008, S105
from __future__ import annotations

import argparse
import datetime
import uvicorn
import fastapi
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

def build_vulnerable_app():
    """Minimal FastAPI app with HS256 JWT, no expiry check, no rate limiting."""

    SECRET = "password"
    ALGORITHM = "HS256"
    USERS = {"admin": "admin123", "alice": "alice456"}

    app = fastapi.FastAPI(title="Vulnerable Demo (Exp 2)")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

    @app.post("/login")
    def login(form: OAuth2PasswordRequestForm = Depends()):
        if USERS.get(form.username) != form.password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = jwt.encode({"sub": form.username, "role": "user"}, SECRET, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}

    @app.get("/protected")
    def protected(token: str = Depends(oauth2_scheme)):
        try:
            # Check what algorithm the incoming attack token is using
            headers = jwt.get_unverified_header(token)
            incoming_alg = headers.get("alg", "").lower()
        
            if incoming_alg == "none":
                # Explicitly drop signature verification constraints for the exploit simulation
                payload = jwt.decode(token, options={"verify_signature": False})
            else:
                payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
            
            return {"user": payload.get("sub")}
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=str(e))

    @app.get("/admin")
    def admin(token: str = Depends(oauth2_scheme)):
        try:
            # Check what algorithm the incoming attack token is using
            headers = jwt.get_unverified_header(token)
            incoming_alg = headers.get("alg", "").lower()
        
            if incoming_alg == "none":
                # Drop signature and expiration checks for the exploit simulation
                payload = jwt.decode(token, options={"verify_signature": False, "verify_exp": False})
            else:
                payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM], options={"verify_exp": False})
            
            # Keep your existing role check intact
            if payload.get("role") != "admin":
                raise HTTPException(status_code=403, detail="Not admin")
            
            return {"message": "Welcome, admin"}
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=str(e))

    return app


def build_hardened_app():
    """Hardened FastAPI app: RS256 JWT, Argon2id, rate limiting, expiry."""
    import fastapi
    import jwt
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from fastapi import Depends, HTTPException
    from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware

    from presidio_fastapi import FastAPI
    from presidio_fastapi.rate_limit import limiter

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )
    public_pem = public_key.public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )

    try:
        from argon2 import PasswordHasher

        _ph = PasswordHasher()

        def verify_password(plain: str, hashed: str) -> bool:
            try:
                return _ph.verify(hashed, plain)
            except Exception:
                return False

        _USERS = {
            "admin": _ph.hash("admin123"),
            "alice": _ph.hash("alice456"),
        }
    except ImportError:
        import hashlib
        import hmac

        def verify_password(plain: str, hashed: str) -> bool:
            return hmac.compare_digest(hashlib.sha256(plain.encode()).hexdigest(), hashed)

        _USERS = {
            "admin": hashlib.sha256(b"admin123").hexdigest(),
            "alice": hashlib.sha256(b"alice456").hexdigest(),
        }

    app = FastAPI(title="Hardened Demo (Exp 2)")
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

    @app.post("/login")
    @limiter.limit("5/minute")
    def login(request: fastapi.Request, form: OAuth2PasswordRequestForm = Depends()):
        hashed = _USERS.get(form.username)
        if not hashed or not verify_password(form.password, hashed):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        exp = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        token = jwt.encode(
            {"sub": form.username, "role": "user", "exp": exp, "iss": "presidio-ids"},
            private_pem,
            algorithm="RS256",
        )
        return {"access_token": token, "token_type": "bearer"}

    @app.get("/protected")
    def protected(token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(
                token, public_pem, algorithms=["RS256"], options={"require": ["exp", "iss"]}
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=str(e))
        return {"user": payload.get("sub"), "role": payload.get("role")}

    @app.get("/admin")
    def admin(token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(
                token, public_pem, algorithms=["RS256"], options={"require": ["exp", "iss"]}
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=str(e))
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not admin")
        return {"message": "Welcome, admin"}

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment 2 — JWT/Auth demo server")
    parser.add_argument("--mode", choices=["vulnerable", "hardened"], required=True)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.mode == "vulnerable":
        print(
            f"[Vulnerable mode] Starting on port {args.port} — HS256, secret='password', no expiry"
        )
        app = build_vulnerable_app()
    else:
        print(f"[Hardened mode] Starting on port {args.port} — RS256, Argon2id, rate limiting")
        app = build_hardened_app()

    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
