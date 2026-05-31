"""JWT encode/decode utilities using HS256."""

from datetime import UTC, datetime, timedelta

from jose import ExpiredSignatureError, jwt
from jose import JWTError as _JoseJWTError


class ExpiredTokenError(Exception):
    """Raised when a JWT has expired."""


class InvalidTokenError(Exception):
    """Raised when a JWT cannot be decoded (wrong key, tampered, malformed)."""


def encode_token(subject: str, *, secret: str, algorithm: str, ttl_minutes: int) -> str:
    """Encode a JWT with *subject* as the ``sub`` claim."""
    exp = datetime.now(UTC) + timedelta(minutes=ttl_minutes)
    return jwt.encode({"sub": subject, "exp": exp}, secret, algorithm=algorithm)


def decode_token(token: str, *, secret: str, algorithm: str) -> dict:
    """Decode a JWT and return its payload.

    Raises:
        ExpiredTokenError: if the token's ``exp`` claim is in the past.
        InvalidTokenError: if the signature is invalid or the token is malformed.
    """
    try:
        return jwt.decode(token, secret, algorithms=[algorithm])
    except ExpiredSignatureError as exc:
        raise ExpiredTokenError from exc
    except _JoseJWTError as exc:
        raise InvalidTokenError from exc
