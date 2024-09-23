from typing import Optional, List
import uuid
from datetime import datetime
from pydantic import BaseModel


class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class PortfolioInDBBase(PortfolioBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PortfolioPublic(PortfolioInDBBase):
    pass


class PortfoliosPublic(BaseModel):
    data: List[PortfolioPublic]


class PortfolioInDB(PortfolioInDBBase):
    pass
