from datetime import datetime
from enum import Enum
from typing import Optional

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


class TradeMetrics(BaseModel):
    average_trade_volume: Optional[float]
    trade_frequency_days_per_trade: Optional[float]
    trade_frequency_trades_per_day: Optional[float]
    average_holding_period_days: Optional[float]
    win_loss_ratio: Optional[float]

    class Config:
        from_attributes = True


class Period(str, Enum):
    ONE_DAY = "1D"
    ONE_WEEK = "1W"
    ONE_MONTH = "1M"
    THREE_MONTHS = "3M"
    SIX_MONTHS = "6M"
    ONE_YEAR = "1Y"
    THREE_YEARS = "3Y"
    FIVE_YEARS = "5Y"
    TEN_YEARS = "10Y"
    YEAR_TO_DATE = "YTD"
    ALL = "All"
