from app.auth.passwords import hash_password, verify_password


def test_hash_password_returns_hash():
    password = "StrongPassword123!"

    hashed = hash_password(password)

    assert hashed != password
    assert isinstance(hashed, str)
    assert hashed


def test_verify_password_with_correct_password():
    password = "StrongPassword123!"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_with_wrong_password():
    password = "StrongPassword123!"
    hashed = hash_password(password)

    assert verify_password("WrongPassword123!", hashed) is False


def test_hash_password_produces_different_hashes():
    password = "StrongPassword123!"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash
    assert verify_password(password, first_hash) is True
    assert verify_password(password, second_hash) is True