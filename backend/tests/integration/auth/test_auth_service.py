import pytest
from app.auth.service import AuthenticationService
from app.auth.schemas import RegisterRequest, LoginRequest
from app.core.exceptions import AppException
from tests.factories.user_factory import UserFactory


@pytest.mark.asyncio
class TestAuthenticationServiceIntegration:

    async def test_service_registers_user_successfully(self, db_session):
        # Arrange
        service = AuthenticationService(db_session)
        registration_data = RegisterRequest(
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@unitedstaffing.ai",
            password="SecurePassword123!"
        )

        # Act
        persisted_user = await service.register(registration_data)

        # Assert
        assert persisted_user.id is not None
        assert persisted_user.email == registration_data.email
        assert persisted_user.hashed_password != registration_data.password

    async def test_service_registration_raises_conflict_for_duplicate_email(self, db_session, sample_user):
        # Arrange
        service = AuthenticationService(db_session)
        duplicate_data = RegisterRequest(
            first_name="Duplicate",
            last_name="User",
            email=sample_user.email,  # Reusing the existing user's email address
            password="Password123!"
        )

        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await service.register(duplicate_data)
        
        assert exc_info.value.status_code == 409
        assert "already registered" in exc_info.value.message