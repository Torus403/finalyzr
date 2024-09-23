import uuid
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    String,
    Numeric,
    DateTime,
    Enum,
    ForeignKey,
)
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship

from app.core.db import Base


class CashActionType(str, PyEnum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


class CashAction(Base):
    __tablename__ = "cash_actions"

    id = Column(
        CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    action = Column(Enum(CashActionType, native_enum=False), nullable=False)
    amount = Column(Numeric(20, 10), nullable=False)
    execution_timestamp = Column(DateTime(timezone=True), nullable=False)
    currency = Column(String(3), nullable=False)
    notes = Column(String(1000), nullable=True)
    portfolio_id = Column(CHAR(36), ForeignKey("portfolios.id"), nullable=False)

    portfolio = relationship("Portfolio", back_populates="cash_actions")
