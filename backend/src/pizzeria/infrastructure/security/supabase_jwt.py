"""Verification of Supabase Auth access tokens against the project's JWKS (ADR 0001)."""

from collections.abc import Callable
from typing import Any

import jwt

# Asymmetric signing keys only; tokens signed with the legacy shared secret are rejected.
_ALGORITHMS = ["ES256", "RS256"]
_AUDIENCE = "authenticated"

# Given a raw token, returns the public key that should have signed it.
KeySource = Callable[[str], Any]


class ExpiredTokenError(Exception):
    """Raised when an access token has expired."""


class InvalidTokenError(Exception):
    """Raised when an access token is malformed, untrusted, or meant for someone else."""


def jwks_key_source(jwks_url: str) -> KeySource:
    """Key source backed by Supabase's JWKS endpoint; keys are cached for 10 minutes."""
    client = jwt.PyJWKClient(jwks_url, cache_keys=True, lifespan=600)
    return lambda token: client.get_signing_key_from_jwt(token).key


def verify_access_token(token: str, *, key_source: KeySource, issuer: str) -> dict:
    """Verify signature, expiry, audience and issuer, and return the token's claims.

    Raises:
        ExpiredTokenError: if the token's ``exp`` claim is in the past.
        InvalidTokenError: for any other reason the token can't be trusted.
    """
    try:
        return jwt.decode(
            token,
            key_source(token),
            algorithms=_ALGORITHMS,
            audience=_AUDIENCE,
            issuer=issuer,
            options={"require": ["exp", "sub", "aud", "iss"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise ExpiredTokenError from exc
    except (jwt.InvalidTokenError, jwt.PyJWKClientError) as exc:
        raise InvalidTokenError from exc
