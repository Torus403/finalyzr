import uuid
from typing import Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[uuid.UUID] = None


class Message(BaseModel):
    message: str


class NewPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


class PasswordResetResponse(BaseModel):
    token: str
