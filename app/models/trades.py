import uuid
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    Enum,
    Numeric,
)
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship

from app.core.db import Base


class ActionType(str, PyEnum):
    BUY = "buy"
    SELL = "sell"


class Trade(Base):
    __tablename__ = "trades"

    id = Column(
        CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    action = Column(Enum(ActionType, native_enum=False), nullable=False)
    execution_timestamp = Column(DateTime(timezone=True), nullable=False)
    ticker = Column(String(10), nullable=False)
    price = Column(Numeric(20, 10), nullable=False)
    quantity = Column(Numeric(20, 10), nullable=False)
    currency = Column(String(3), nullable=False)
    notes = Column(String(1000), nullable=True)
    portfolio_id = Column(CHAR(36), ForeignKey("portfolios.id"), nullable=False)

    portfolio = relationship("Portfolio", back_populates="trades")
