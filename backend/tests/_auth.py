"""Helpers for signing Supabase-shaped access tokens in tests (no network)."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt
from cryptography.hazmat.primitives.asymmetric import ec

ISSUER = "https://test-project.supabase.co/auth/v1"


def make_key() -> ec.EllipticCurvePrivateKey:
    """A fresh ES256 key pair, standing in for the Supabase project's signing key."""
    return ec.generate_private_key(ec.SECP256R1())


def sign_token(
    key: ec.EllipticCurvePrivateKey,
    *,
    role: str | None = "menu_manager",
    email: str = "manager@pizzeria.test",
    expires_in: timedelta = timedelta(hours=1),
    **overrides: Any,
) -> str:
    claims: dict[str, Any] = {
        "sub": str(uuid4()),
        "email": email,
        "aud": "authenticated",
        "iss": ISSUER,
        "exp": datetime.now(UTC) + expires_in,
        "role": "authenticated",
        "app_metadata": {"role": role} if role else {},
    }
    claims.update(overrides)
    return jwt.encode(claims, key, algorithm="ES256")
