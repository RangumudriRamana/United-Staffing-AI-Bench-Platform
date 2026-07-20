import pytest

@pytest.mark.asyncio
class TestRegistrationAPI:

    async def test_api_registration_success(self, client):
        # Arrange
        payload = {
            "first_name": "Alex",
            "last_name": "Smith",
            "email": "alex.smith@unitedstaffing.ai",
            "password": "StrongPassword123!"
        }

        # Act
        response = await client.post("/api/v1/auth/register", json=payload)
        response_json = response.json()

        # Assert
        assert response.status_code == 211 or response.status_code == 201
        assert response_json["success"] is True
        assert "user" in response_json["data"]
        assert response_json["data"]["user"]["email"] == payload["email"]
        assert "password" not in response_json["data"]["user"], "Plaintext passwords must never exit the domain wrapper."