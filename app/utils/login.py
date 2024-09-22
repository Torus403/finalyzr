from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_password
from app.crud.users import get_user_by_email
from app.models.users import User


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None


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
