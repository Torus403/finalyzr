import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.mysql import CHAR
from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(CHAR(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_superuser = Column(Boolean, nullable=False, default=False)
