from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.core.security import verify_password
from app.schemas.users import UserCreate, UserUpdate
from app.services.users import (
    authenticate_user,
    create_user,
    update_user,
    update_user_password,
)


def test_authenticate_user_success(db: Session, create_user_fixture):
    hashed_password = hash_password("testpassword")
    user = create_user_fixture(email="testuser@example.com", password=hashed_password)
    authenticated_user = authenticate_user(
        session=db, email="testuser@example.com", password="testpassword"
    )
    assert authenticated_user is not None
    assert authenticated_user.email == user.email


def test_authenticate_user_invalid_password(db: Session, create_user_fixture):
    hashed_password = hash_password("testpassword")
    create_user_fixture(email="testuser@example.com", password=hashed_password)
    authenticated_user = authenticate_user(
        session=db, email="testuser@example.com", password="wrongpassword"
    )
    assert authenticated_user is None


def test_authenticate_user_not_found(db: Session):
    authenticated_user = authenticate_user(
        session=db, email="nonexistent@example.com", password="testpassword"
    )
    assert authenticated_user is None


def test_create_user_success(db: Session):
    user_create = UserCreate(email="newuser@example.com", password="newpassword")
    new_user = create_user(session=db, user_create=user_create)
    assert new_user.email == "newuser@example.com"
    assert verify_password("newpassword", new_user.password)


def test_update_user_success(db: Session, create_user_fixture):
    hashed_password = hash_password("oldpassword")
    user = create_user_fixture(email="olduser@example.com", password=hashed_password)
    user_update = UserUpdate(email="updateduser@example.com")
    updated_user = update_user(session=db, current_user=user, new_user=user_update)
    assert updated_user.email == "updateduser@example.com"


def test_update_user_password_success(db: Session, create_user_fixture):
    hashed_password = hash_password("oldpassword")
    user = create_user_fixture(email="testuser@example.com", password=hashed_password)
    updated_user = update_user_password(session=db, user=user, password="newpassword")
    assert verify_password("newpassword", updated_user.password)


def test_update_user_password_invalidates_old_password(
    db: Session, create_user_fixture
):
    hashed_password = hash_password("oldpassword")
    user = create_user_fixture(email="testuser@example.com", password=hashed_password)
    update_user_password(session=db, user=user, password="newpassword")
    assert not verify_password("oldpassword", user.password)
