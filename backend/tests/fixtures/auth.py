import pytest
from app.auth.security import create_access_token
from app.models.user import User


def create_test_token(user: User) -> str:
    """Programmatically encodes a real cryptographic JWT token payload for a target user object."""
    # Pass the public_id string directly as the subject parameter
    return create_access_token(str(user.public_id))


def authorization_header(token: str) -> dict[str, str]:
    """Generates the standard compliant authorization mapping dictionary."""
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_headers(sample_user):
    """Instantly delivers an active bearer token authorization header mapping for a normal recruiter."""
    token = create_test_token(sample_user)
    return authorization_header(token)


@pytest.fixture
def admin_headers(sample_admin):
    """Instantly delivers an active bearer token authorization header mapping for an administrative profile."""
    token = create_test_token(sample_admin)
    return authorization_header(token)