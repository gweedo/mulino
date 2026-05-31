"""Unit tests for password hashing utilities."""

from pizzeria.infrastructure.security.passwords import hash_password, verify_password


def test_hash_returns_argon2_string():
    result = hash_password("secret")
    assert isinstance(result, str)
    assert result.startswith("$argon2")


def test_hash_is_non_deterministic():
    h1 = hash_password("secret")
    h2 = hash_password("secret")
    assert h1 != h2


def test_verify_correct_password_returns_true():
    hashed = hash_password("correct")
    assert verify_password("correct", hashed) is True


def test_verify_wrong_password_returns_false():
    hashed = hash_password("correct")
    assert verify_password("wrong", hashed) is False


def test_verify_empty_password_returns_false():
    hashed = hash_password("correct")
    assert verify_password("", hashed) is False
