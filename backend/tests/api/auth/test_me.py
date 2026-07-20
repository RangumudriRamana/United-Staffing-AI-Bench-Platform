import pytest

@pytest.mark.asyncio
class TestCurrentProfileAPI:

    async def test_get_current_user_profile_when_authenticated(self, client, user_headers, sample_user):
        # Arrange & Act
        response = await client.get("/api/v1/auth/me", headers=user_headers)
        response_json = response.json()

        # Assert
        assert response.status_code == 200
        assert response_json["success"] is True
        assert response_json["data"]["user"]["email"] == sample_user.email

    async def test_get_profile_fails_without_authorization_header(self, client):
        # Arrange & Act
        response = await client.get("/api/v1/auth/me")

        # Assert
        assert response.status_code == 403