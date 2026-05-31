"""Unit tests for JWT encode/decode utilities."""

from datetime import UTC, datetime, timedelta

from jose import jwt as _jose_jwt

from pizzeria.infrastructure.security.jwt import (
    ExpiredTokenError,
    InvalidTokenError,
    decode_token,
    encode_token,
)

_SECRET = "test-secret"
_ALG = "HS256"


def test_encode_returns_string():
    token = encode_token("user@example.com", secret=_SECRET, algorithm=_ALG, ttl_minutes=30)
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_returns_payload_dict():
    token = encode_token("user@example.com", secret=_SECRET, algorithm=_ALG, ttl_minutes=30)
    payload = decode_token(token, secret=_SECRET, algorithm=_ALG)
    assert isinstance(payload, dict)


def test_decode_round_trips_subject():
    token = encode_token("user@example.com", secret=_SECRET, algorithm=_ALG, ttl_minutes=30)
    payload = decode_token(token, secret=_SECRET, algorithm=_ALG)
    assert payload["sub"] == "user@example.com"


def test_expired_token_raises_ExpiredTokenError():
    # Craft a token with a past exp using jose directly — no sleep needed.
    past_exp = datetime.now(UTC) - timedelta(seconds=1)
    token = _jose_jwt.encode({"sub": "x", "exp": past_exp}, _SECRET, algorithm=_ALG)
    try:
        decode_token(token, secret=_SECRET, algorithm=_ALG)
        raise AssertionError("Expected ExpiredTokenError")
    except ExpiredTokenError:
        pass


def test_tampered_token_raises_InvalidTokenError():
    token = encode_token("user@example.com", secret=_SECRET, algorithm=_ALG, ttl_minutes=30)
    tampered = token[:-4] + "XXXX"
    try:
        decode_token(tampered, secret=_SECRET, algorithm=_ALG)
        raise AssertionError("Expected InvalidTokenError")
    except InvalidTokenError:
        pass


def test_wrong_secret_raises_InvalidTokenError():
    token = encode_token("user@example.com", secret=_SECRET, algorithm=_ALG, ttl_minutes=30)
    try:
        decode_token(token, secret="wrong-secret", algorithm=_ALG)
        raise AssertionError("Expected InvalidTokenError")
    except InvalidTokenError:
        pass


def test_expired_error_is_not_invalid_error():
    assert not issubclass(ExpiredTokenError, InvalidTokenError)
    assert not issubclass(InvalidTokenError, ExpiredTokenError)
