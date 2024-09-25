import uuid
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.users import User


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Retrieve a user by their email address."""
    stmt = select(User).where(User.email == email)
    return session.execute(stmt).scalar_one_or_none()


def get_user_by_id(session: Session, user_id: uuid.UUID) -> Optional[User]:
    """Retrieve a user by their unique ID."""
    return session.get(User, user_id)


def get_users(session: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Retrieve a list of users with pagination."""
    stmt = select(User).offset(skip).limit(limit)
    return list(session.execute(stmt).scalars().all())


def get_user_count(session: Session) -> int:
    """Get the total number of users."""
    stmt = select(func.count()).select_from(User)
    return session.execute(stmt).scalar_one()


def create_user(session: Session, user_data: dict) -> User:
    """
    Create a new user in the database.
    """
    user = User(**user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user(session: Session, user: User, updates: dict) -> User:
    """
    Update an existing user's information.
    """
    for key, value in updates.items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, user: User) -> None:
    """
    Delete a user from the database.
    """
    session.delete(user)
    session.commit()
