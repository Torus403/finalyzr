import uuid

from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.mysql import CHAR

from sqlalchemy.orm import relationship

from app.core.db import Base


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(
        CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    name = Column(String(255), index=True, nullable=False)
    description = Column(String(500), nullable=True)
    owner_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="portfolios")
