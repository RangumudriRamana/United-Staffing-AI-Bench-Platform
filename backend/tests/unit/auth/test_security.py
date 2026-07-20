import pytest
from jwt import PyJWTError
from uuid import uuid4

from app.auth.security import create_access_token, decode_access_token, hash_password, verify_password


class TestSecurityUtilities:
    
    def test_password_hashing_and_verification(self):
        # Arrange
        plaintext_password = "SuperSecurePassword123!"
        wrong_password = "WrongPassword123!"

        # Act
        hashed = hash_password(plaintext_password)
        is_valid = verify_password(plaintext_password, hashed)
        is_invalid = verify_password(wrong_password, hashed)

        # Assert
        assert hashed != plaintext_password, "Password hash must not match plaintext."
        assert is_valid is True, "Valid password verification failed."
        assert is_invalid is False, "Verification should fail for incorrect passwords."

    def test_password_salting_uniqueness(self):
        # Arrange
        password = "IdenticalPassword123!"

        # Act
        hash_one = hash_password(password)
        hash_two = hash_password(password)

        # Assert
        assert hash_one != hash_two, "Proper salting must produce distinct hashes for identical inputs."

    def test_jwt_token_encoding_and_decoding_happy_path(self):
        # Arrange
        user_id = str(uuid4())

        # Act: Pass the string directly as the subject
        token = create_access_token(user_id)
        decoded_payload = decode_access_token(token)

        # Assert
        assert decoded_payload.get("sub") == user_id
        assert "exp" in decoded_payload, "Expiration claim ('exp') must be automatically attached."

    def test_jwt_token_decoding_fails_when_tampered(self):
        # Arrange
        user_id = str(uuid4())
        # Pass the string directly
        token = create_access_token(user_id)
        
        # Act
        tampered_token = token[:-3] + "xyz"

        # Assert
        with pytest.raises(PyJWTError):
            decode_access_token(tampered_token)