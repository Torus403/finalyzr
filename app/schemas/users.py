import uuid
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str


# class UserUpdate(UserBase):
#     password: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserPublic(UserBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


class UsersPublic(BaseModel):
    data: List[UserPublic]
    count: int


class UpdatePassword(BaseModel):
    current_password: str
    new_password: str


class Message(BaseModel):
    message: str
