from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.core.security import verify_password
from app.crud import users as crud_users
from app.crud.users import get_user_by_email
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    """
    Authenticate a user by email and password.
    """
    user = get_user_by_email(session=session, email=email)
    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user


def create_user(session: Session, user_create: UserCreate) -> User:
    """
    Create a new user with hashed password.
    """
    user_data = user_create.model_dump(exclude={"password"})
    user_data["password"] = hash_password(user_create.password)
    return crud_users.create_user(session, user_data)


def update_user(session: Session, current_user: User, new_user: UserUpdate) -> User:
    """
    Update an existing user's information.
    """
    update_data = new_user.model_dump(exclude_unset=True)
    return crud_users.update_user(session, current_user, update_data)


def update_user_password(session: Session, user: User, password: str) -> User:
    """
    Update a user's password with hashing.
    """
    hashed_password = hash_password(password)
    return crud_users.update_user(session, user, {"password": hashed_password})
