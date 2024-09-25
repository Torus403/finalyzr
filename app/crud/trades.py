import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.trades import Trade


def get_trade_by_id(session: Session, trade_id: uuid.UUID) -> Optional[Trade]:
    """Retrieve trade by its id."""
    return (
        session.execute(select(Trade).where(Trade.id == str(trade_id)))
        .scalars()
        .first()
    )


def get_trades_by_portfolio(
    session: Session, portfolio_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> List[Trade]:
    """Retrieve all trades from a portfolio with pagination."""
    stmt = select(Trade).where(Trade.portfolio_id == str(portfolio_id)).offset(skip).limit(limit)
    return list(session.execute(stmt).scalars().all())


def create_trade(session: Session, trade_data: dict) -> Trade:
    """Create a new trade in the database."""
    trade = Trade(**trade_data)
    session.add(trade)
    session.commit()
    session.refresh(trade)
    return trade


def update_trade(session: Session, trade: Trade, updates: dict) -> Trade:
    """Update an existing trade."""
    for key, value in updates.items():
        setattr(trade, key, value)
    session.add(trade)
    session.commit()
    session.refresh(trade)
    return trade


def delete_trade(session: Session, trade: Trade) -> None:
    """Delete a trade from the database."""
    session.delete(trade)
    session.commit()
