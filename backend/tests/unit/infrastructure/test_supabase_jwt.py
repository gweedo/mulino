from datetime import timedelta

import jwt
import pytest

from pizzeria.infrastructure.security.supabase_jwt import (
    ExpiredTokenError,
    InvalidTokenError,
    verify_access_token,
)
from tests._auth import ISSUER, make_key, sign_token


@pytest.fixture
def key():
    return make_key()


def _verify(token: str, key) -> dict:
    return verify_access_token(token, key_source=lambda _t: key.public_key(), issuer=ISSUER)


def test_valid_token_returns_claims(key):
    claims = _verify(sign_token(key, email="a@example.com"), key)
    assert claims["email"] == "a@example.com"
    assert claims["app_metadata"] == {"role": "menu_manager"}


def test_expired_token_raises_expired(key):
    with pytest.raises(ExpiredTokenError):
        _verify(sign_token(key, expires_in=timedelta(minutes=-1)), key)


def test_wrong_audience_is_invalid(key):
    with pytest.raises(InvalidTokenError):
        _verify(sign_token(key, aud="anon"), key)


def test_wrong_issuer_is_invalid(key):
    with pytest.raises(InvalidTokenError):
        _verify(sign_token(key, iss="https://evil.example/auth/v1"), key)


def test_token_signed_by_other_key_is_invalid(key):
    with pytest.raises(InvalidTokenError):
        _verify(sign_token(make_key()), key)


def test_hs256_token_is_rejected(key):
    """Symmetric tokens (legacy JWT secret) are never accepted — asymmetric keys only."""
    token = jwt.encode(
        {"sub": "x", "aud": "authenticated", "iss": ISSUER, "exp": 9999999999},
        "shared-secret-at-least-32-bytes-long!!",
        algorithm="HS256",
    )
    with pytest.raises(InvalidTokenError):
        _verify(token, key)


def test_malformed_token_is_invalid(key):
    with pytest.raises(InvalidTokenError):
        _verify("not-a-jwt", key)


def test_key_lookup_failure_is_invalid():
    """An unknown `kid` (JWKS lookup error) surfaces as InvalidTokenError, not a 500."""

    def failing_source(_token: str):
        raise jwt.PyJWKClientError("Unable to find a signing key")

    with pytest.raises(InvalidTokenError):
        verify_access_token(sign_token(make_key()), key_source=failing_source, issuer=ISSUER)
