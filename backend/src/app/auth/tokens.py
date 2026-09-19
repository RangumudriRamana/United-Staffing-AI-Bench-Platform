from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt

from app.core.config import get_settings

settings = get_settings()


def create_access_token(
    subject: UUID,
) -> tuple[str, str]:
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes,
    )

    jti = str(uuid4())

    payload = {
        "sub": str(subject),
        "jti": jti,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return token, jti


def decode_access_token(
    token: str,
) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )