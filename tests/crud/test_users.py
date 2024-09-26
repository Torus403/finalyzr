import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import app.crud.users as user_crud
from app.models.users import User
from tests.utils.random_data import generate_random_email, generate_random_password


def test_create_user_success(db: Session, create_user_fixture):
    user = create_user_fixture()
    assert user.email is not None
    assert hasattr(user, "password")
    assert user.id is not None


def test_create_user_duplicate_email(db: Session, create_user_fixture):
    email = generate_random_email()
    create_user_fixture(email=email)
    with pytest.raises(IntegrityError):
        create_user_fixture(email=email)


def test_get_user_by_email_exists(db: Session, create_user_fixture):
    user = create_user_fixture()
    fetched_user = user_crud.get_user_by_email(session=db, email=user.email)
    assert fetched_user is not None
    assert fetched_user.email == user.email


def test_get_user_by_email_not_exists(db: Session):
    email = generate_random_email()
    fetched_user = user_crud.get_user_by_email(session=db, email=email)
    assert fetched_user is None


def test_get_user_by_id_exists(db: Session, create_user_fixture):
    user = create_user_fixture()
    fetched_user = user_crud.get_user_by_id(session=db, user_id=user.id)
    assert fetched_user is not None
    assert fetched_user.id == user.id


def test_get_user_by_id_not_exists(db: Session):
    non_existent_id = uuid.uuid4()
    fetched_user = user_crud.get_user_by_id(session=db, user_id=non_existent_id)
    assert fetched_user is None


def test_get_users_empty(db: Session):
    users = user_crud.get_users(session=db)
    assert len(users) == 0


def test_get_users_default_pagination(db: Session, create_multiple_users_fixture):
    created_users = create_multiple_users_fixture(5)
    fetched_users = user_crud.get_users(session=db)
    assert len(fetched_users) == 5
    assert all(user in fetched_users for user in created_users)


def test_get_users_custom_pagination(db: Session, create_multiple_users_fixture):
    create_multiple_users_fixture(10)
    fetched_users = user_crud.get_users(session=db, skip=5, limit=3)
    assert len(fetched_users) == 3


def test_get_user_count(db: Session, create_multiple_users_fixture):
    create_multiple_users_fixture(7)
    count = user_crud.get_user_count(session=db)
    assert count == 7


def test_update_user_success(db: Session, create_user_fixture):
    user = create_user_fixture()
    new_email = generate_random_email()
    new_password = generate_random_password()
    updates = {"email": new_email, "password": new_password}
    updated_user = user_crud.update_user(session=db, user=user, updates=updates)
    assert updated_user.email == new_email
    assert updated_user.password == new_password


def test_update_user_partial(db: Session, create_user_fixture):
    user = create_user_fixture()
    original_email = user.email
    new_password = generate_random_password()
    updates = {"password": new_password}
    updated_user = user_crud.update_user(session=db, user=user, updates=updates)
    assert updated_user.email == original_email
    assert updated_user.password == new_password


def test_delete_user_success(db: Session, create_user_fixture):
    user = create_user_fixture()
    user_crud.delete_user(session=db, user=user)
    fetched_user = user_crud.get_user_by_id(session=db, user_id=user.id)
    assert fetched_user is None


def test_delete_user_not_in_db(db: Session):
    non_existent_user = User(
        id=uuid.uuid4(),
        email=generate_random_email(),
        password=generate_random_password(),
    )
    with pytest.raises(Exception):
        user_crud.delete_user(session=db, user=non_existent_user)


@pytest.mark.parametrize(
    "user_count,skip,limit,expected_count",
    [
        (10, 0, 5, 5),
        (10, 5, 10, 5),
        (5, 0, 10, 5),
        (5, 10, 10, 0),
    ],
)
def test_get_users_pagination(
    db: Session, create_multiple_users_fixture, user_count, skip, limit, expected_count
):
    create_multiple_users_fixture(user_count)
    users = user_crud.get_users(session=db, skip=skip, limit=limit)
    assert len(users) == expected_count


def test_get_user_count_empty_db(db: Session):
    count = user_crud.get_user_count(session=db)
    assert count == 0


def test_update_user_to_existing_email(db: Session, create_multiple_users_fixture):
    users = create_multiple_users_fixture(2)
    with pytest.raises(IntegrityError):
        user_crud.update_user(
            session=db, user=users[0], updates={"email": users[1].email}
        )
