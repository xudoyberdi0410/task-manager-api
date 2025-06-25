import pytest
from fastapi import HTTPException
from src.services.auth_service import AuthService, UserService
from src.repositories.user_repository import UserRepository


@pytest.fixture
def auth_service(db_session):
    return AuthService(db_session)


@pytest.fixture
def user_service(db_session):
    return UserService(db_session)


def test_authenticate_user_success(auth_service, db_session):
    repo = UserRepository(db_session)
    email = "auth_test@example.com"
    username = "auth_test_user"
    password = "password"
    repo.create_user(email, username, password)

    authenticated_user = auth_service.authenticate_user(email, password)
    assert authenticated_user is not None
    assert authenticated_user.email == email

    authenticated_user_by_username = auth_service.authenticate_user(username, password)
    assert authenticated_user_by_username is not None
    assert authenticated_user_by_username.username == username


def test_authenticate_user_failure(auth_service):
    assert auth_service.authenticate_user("wrong@email.com", "wrongpassword") is None


def test_login_success(auth_service, db_session):
    repo = UserRepository(db_session)
    email = "login_test@example.com"
    username = "login_test_user"
    password = "password"
    repo.create_user(email, username, password)

    result = auth_service.login(email, password)
    assert "access_token" in result
    assert result["token_type"] == "bearer"


def test_login_failure(auth_service):
    with pytest.raises(HTTPException) as excinfo:
        auth_service.login("wrong@email.com", "wrongpassword")
    assert excinfo.value.status_code == 401


def test_get_all_users(user_service, db_session):
    repo = UserRepository(db_session)
    repo.create_user("service_test1@example.com", "service_user1", "pass")
    repo.create_user("service_test2@example.com", "service_user2", "pass")

    result = user_service.get_all_users()
    assert result["total"] >= 2
    assert len(result["users"]) >= 2


def test_search_users(user_service, db_session):
    repo = UserRepository(db_session)
    repo.create_user("search_service1@example.com", "search_service_user1", "pass")
    repo.create_user("another@example.com", "search_service_user2", "pass")

    result = user_service.search_users(query="search_service")
    assert result["total"] == 2
    assert len(result["users"]) == 2


def test_register_user_success(user_service):
    email = "register_test@example.com"
    username = "register_test_user"
    password = "password"

    new_user = user_service.register_user(email, username, password)
    assert new_user is not None
    assert new_user.email == email


def test_register_user_email_exists(user_service, db_session):
    repo = UserRepository(db_session)
    email = "existing@example.com"
    username = "existing_user"
    password = "password"
    repo.create_user(email, username, password)

    with pytest.raises(HTTPException) as excinfo:
        user_service.register_user(email, "new_username", password)
    assert excinfo.value.status_code == 400
