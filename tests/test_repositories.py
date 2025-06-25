from src.models.user import User
from src.repositories.user_repository import UserRepository


def test_create_user(db_session):
    repo = UserRepository(db_session)
    email = "test@example.com"
    username = "testuser"
    password = "password"

    new_user = repo.create_user(email, username, password)

    assert new_user.email == email
    assert new_user.username == username
    assert new_user.hashed_password is not None

    db_user = db_session.query(User).filter(User.email == email).first()
    assert db_user is not None
    assert db_user.username == username


def test_get_by_email(db_session):
    repo = UserRepository(db_session)
    email = "get_by_email@example.com"
    username = "get_by_email_user"
    password = "password"
    repo.create_user(email, username, password)

    user = repo.get_by_email(email)

    assert user is not None
    assert user.email == email


def test_get_by_id(db_session):
    repo = UserRepository(db_session)
    email = "get_by_id@example.com"
    username = "get_by_id_user"
    password = "password"
    new_user = repo.create_user(email, username, password)

    user = repo.get_by_id(new_user.user_id)

    assert user is not None
    assert user.user_id == new_user.user_id


def test_get_by_username(db_session):
    repo = UserRepository(db_session)
    email = "get_by_username@example.com"
    username = "get_by_username_user"
    password = "password"
    repo.create_user(email, username, password)

    user = repo.get_by_username(username)

    assert user is not None
    assert user.username == username


def test_get_all_users(db_session):
    repo = UserRepository(db_session)
    db_session.query(User).delete()
    db_session.commit()
    repo.create_user("test1@example.com", "testuser1", "pass")
    repo.create_user("test2@example.com", "testuser2", "pass")

    users, total = repo.get_all()

    assert total == 2
    assert len(users) == 2


def test_search_users(db_session):
    repo = UserRepository(db_session)
    db_session.query(User).delete()
    db_session.commit()
    repo.create_user("search1@example.com", "searchuser1", "pass")
    repo.create_user("search2@example.com", "anotheruser", "pass")

    users, total = repo.search_users(query="search")

    assert total == 2
    assert len(users) == 2


def test_update_user(db_session):
    repo = UserRepository(db_session)
    email = "update@example.com"
    username = "updateuser"
    password = "password"
    new_user = repo.create_user(email, username, password)

    updated_user = repo.update_user(new_user.user_id, username="updated_username")

    assert updated_user is not None
    assert updated_user.username == "updated_username"
    assert updated_user.email == email
