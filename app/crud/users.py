from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.users import User


def get_user_by_email(*, session: Session, email: str) -> User | None:
    return session.execute(
        select(User).filter(User.email == email)
    ).scalar_one_or_none()
