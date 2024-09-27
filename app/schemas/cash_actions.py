import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, condecimal


class ActionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


class CashActionBase(BaseModel):
    action: ActionType
    amount: condecimal(max_digits=20, decimal_places=10)
    execution_timestamp: datetime
    currency: str = Field(..., max_length=3)
    notes: Optional[str] = Field(None, max_length=1000)


class CashActionCreate(CashActionBase):
    pass


class CashActionUpdate(BaseModel):
    action: Optional[ActionType] = None
    amount: Optional[condecimal(max_digits=20, decimal_places=10)] = None
    execution_timestamp: Optional[datetime] = None
    currency: Optional[str] = Field(None, max_length=3)
    notes: Optional[str] = Field(None, max_length=1000)


class CashActionInDBBase(CashActionBase):
    id: uuid.UUID
    portfolio_id: uuid.UUID

    class Config:
        from_attributes = True


class CashAction(CashActionInDBBase):
    pass


class CashActionInDB(CashActionInDBBase):
    pass
