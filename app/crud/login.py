from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.users import User
from app.crud.users import get_user_by_email


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(session=session, email=email)

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user
