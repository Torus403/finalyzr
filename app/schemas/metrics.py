from datetime import datetime

from pydantic import BaseModel


class PortfolioOverview(BaseModel):
    total_portfolio_value: float
    cash_balance: float
    total_open_positions_value: float
    unrealized_returns_percentage: float
    unrealized_returns_absolute: float
    number_of_open_positions: int


class Position(BaseModel):
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    current_value: float
    unrealized_pl: float
    entry_date: datetime


class HistoricalPosition(BaseModel):
    trade_id: str
    symbol: str
    quantity: float
    entry_price: float
    exit_price: float
    realized_pl: float
    entry_date: datetime
    exit_date: datetime
    holding_period_days: int

    class Config:
        from_attributes = True
