from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    is_superuser: bool
