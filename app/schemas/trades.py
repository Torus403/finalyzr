import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, condecimal


class ActionType(str, Enum):
    BUY = "buy"
    SELL = "sell"


class TradeBase(BaseModel):
    action: ActionType
    execution_timestamp: datetime
    ticker: str = Field(..., max_length=10)
    price: condecimal(max_digits=20, decimal_places=10)
    quantity: condecimal(max_digits=20, decimal_places=10)
    currency: str = Field(..., max_length=3)
    notes: Optional[str] = Field(None, max_length=1000)


class TradeCreate(TradeBase):
    pass


class TradeUpdate(BaseModel):
    action: Optional[ActionType] = None
    execution_timestamp: Optional[datetime] = None
    ticker: Optional[str] = Field(None, max_length=10)
    price: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    quantity: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    currency: Optional[str] = Field(None, max_length=3)
    notes: Optional[str] = Field(None, max_length=1000)


class TradeInDBBase(TradeBase):
    id: uuid.UUID
    portfolio_id: uuid.UUID

    class Config:
        from_attributes = True


class Trade(TradeInDBBase):
    pass


class TradeInDB(TradeInDBBase):
    pass
