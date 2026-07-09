# Maintenance Policy — presidio-hardened-fastapi

**Status: Frozen — security-fixes-only** (as of 2026-06-11).

`presidio-hardened-fastapi` is published to PyPI and feature-complete for its scope. It
receives **security fixes only**; no new features are planned. Issues or pull
requests outside the security scope may be closed with a pointer to this policy.

## Not affiliated with Microsoft Presidio

This project is **independent of Microsoft Presidio** (a data-anonymization
toolkit). "Presidio" here refers to the PRESIDIO hardened-component family by
Vladimir Stantchev (GitHub org `presidio-v`).

## Releases & provenance

Releases are published via GitHub Actions **Trusted Publishing** (OIDC — no
stored API tokens) with **PEP 740 attestations**, and every publish is gated by
founder approval (the `release` environment required reviewer).

```bash
pip install presidio-hardened-fastapi
```

PyPI verifies the attached attestations automatically on install for clients
that support PEP 740.

## Reporting security issues

See [`SECURITY.md`](./SECURITY.md).
