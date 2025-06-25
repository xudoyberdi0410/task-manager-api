from src.utils.password import get_password_hash, verify_password


def test_password_hashing():
    password = "plainpassword"
    hashed_password = get_password_hash(password)
    assert hashed_password != password
    assert verify_password(password, hashed_password)
    assert not verify_password("wrongpassword", hashed_password)
