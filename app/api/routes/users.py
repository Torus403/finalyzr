import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

import app.crud.users as user_crud
import app.services.users as user_service
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_superuser,
)
from app.core.security import verify_password
from app.schemas.users import (
    Message,
    UpdatePassword,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
)

router = APIRouter()


@router.post("/signup", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Register a new user.
    """
    existing_user = user_crud.get_user_by_email(session=session, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system",
        )

    user_create = UserCreate(**user_in.model_dump())
    new_user = user_service.create_user(session=session, user_create=user_create)
    return new_user


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
        )
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the current one",
        )

    user_service.update_user_password(
        session=session,
        user=current_user,
        password=body.new_password,
    )
    return Message(message="Password updated successfully")


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdate, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """
    if user_in.email:
        existing_user = user_crud.get_user_by_email(
            session=session, email=user_in.email
        )
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

    updated_user = user_service.update_user(
        session=session, current_user=current_user, new_user=user_in
    )
    return updated_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super users are not allowed to delete themselves",
        )

    user_crud.delete_user(session=session, user=current_user)
    return Message(message="User deleted successfully")


# Superuser endpoints
superuser_router = APIRouter(dependencies=[Depends(get_current_superuser)])


@superuser_router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep
) -> Any:
    """
    Get a specific user by id.
    """
    user = user_crud.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this id does not exist in the system",
        )

    return user


@superuser_router.get(
    "/",
    response_model=UsersPublic,
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """
    user_count = user_crud.get_user_count(session=session)
    users = user_crud.get_users(session=session, skip=skip, limit=limit)
    return UsersPublic(data=users, count=user_count)


@superuser_router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user = user_crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )

    user = user_service.create_user(session=session, user_create=user_in)
    return user


@superuser_router.patch(
    "/{user_id}",
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """
    user = user_crud.get_user_by_id(session=session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = user_crud.get_user_by_email(
            session=session, email=user_in.email
        )
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists"
            )

    updated_user = user_service.update_user(session=session, current_user=user, new_user=user_in)
    return updated_user


@superuser_router.delete("/{user_id}")
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    user = user_crud.get_user_by_id(session=session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Super users are not allowed to delete themselves"
        )

    user_crud.delete_user(session=session, user=user)
    return Message(message="User deleted successfully")
