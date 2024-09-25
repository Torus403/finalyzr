from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

import app.crud.users as user_crud
import app.services.users as user_service
from app.api.deps import SessionDep, get_current_superuser
from app.core import security
from app.core.config import settings
from app.core.security import hash_password
from app.schemas.login import Message, NewPassword, Token

router = APIRouter()


@router.post("/login")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = user_service.authenticate_user(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    return Token(access_token=access_token)


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    email = security.verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )

    user = user_crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this email does not exist in the system.",
        )

    hashed_password = hash_password(password=body.new_password)
    user_service.update_user_password(session=session, user=user, password=hashed_password)

    return Message(message="Password updated successfully")


# Superuser Endpoints
superuser_router = APIRouter(dependencies=[Depends(get_current_superuser)])


@superuser_router.post(
    "/recover-password/{email}",
)
def recover_password_html_content(email: str, session: SessionDep) -> Token:
    """
    HTML Content for Password Recovery
    """
    user = user_crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this username does not exist in the system.",
        )

    password_reset_token = security.generate_password_reset_token(email=email)
    return Token(access_token=password_reset_token)
