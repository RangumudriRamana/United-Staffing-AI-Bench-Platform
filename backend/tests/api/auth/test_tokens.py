import pytest
import jwt
from uuid import uuid4

from app.auth.tokens import create_access_token, decode_access_token
from app.core.config import get_settings


def test_create_access_token_returns_token_and_jti():
    subject = uuid4()

    token, jti = create_access_token(subject)

    assert isinstance(token, str)
    assert token
    assert isinstance(jti, str)
    assert jti


def test_created_token_contains_expected_claims():
    subject = uuid4()

    token, jti = create_access_token(subject)
    payload = decode_access_token(token)

    assert payload["sub"] == str(subject)
    assert payload["jti"] == jti
    assert "exp" in payload


def test_decode_access_token_returns_payload():
    subject = uuid4()

    token, _ = create_access_token(subject)

    payload = decode_access_token(token)

    assert payload["sub"] == str(subject)


def test_decode_access_token_rejects_tampered_token():
    subject = uuid4()

    token, _ = create_access_token(subject)
    tampered_token = token[:-1] + ("a" if token[-1] != "a" else "b")

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(tampered_token)


def test_decode_access_token_rejects_wrong_secret(monkeypatch):
    subject = uuid4()

    token, _ = create_access_token(subject)

    settings = get_settings()
    monkeypatch.setattr(settings, "jwt_secret_key", "wrong-secret")

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)