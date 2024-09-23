import uuid
from sqlalchemy import select, func, delete
from sqlalchemy.orm import Session

from app.models.users import User
from app.schemas.users import UserCreate
from app.core.security import hash_password


def get_user_by_email(*, session: Session, email: str) -> User | None:
    return session.execute(
        select(User).filter(User.email == email)
    ).scalar_one_or_none()


def get_user_count(*, session: Session) -> int:
    count_statement = select(func.count()).select_from(User)
    return session.execute(count_statement).scalar_one()


def get_users(*, session: Session, skip: int = 0, limit: int = 100) -> list[User]:
    statement = select(User).offset(skip).limit(limit)
    return list(session.execute(statement).scalars().all())


def get_user_by_id(session: Session, user_id: uuid.UUID) -> User | None:
    return session.get(User, user_id)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    user_data = user_create.model_dump(exclude={"password"})
    hashed_password = hash_password(user_create.password)
    user_data["password"] = hashed_password

    user = User(**user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user_password(session: Session, user: User, password: str) -> None:
    """
    Update a user's password.
    """
    user.password = password
    session.add(user)
    session.commit()
    session.refresh(user)


def update(session: Session, current_user: User, new_user: dict) -> User:
    for key, value in new_user.items():
        setattr(current_user, key, value)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


def delete_user(session: Session, user: User) -> None:
    session.delete(user)
    session.commit()
