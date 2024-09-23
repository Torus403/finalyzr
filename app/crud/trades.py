from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.trades import Trade
from app.schemas.trades import TradeCreate, TradeUpdate


def get_trade_by_id(session: Session, trade_id: UUID) -> Optional[Trade]:
    return session.execute(select(Trade).where(Trade.id == str(trade_id))).scalars().first()


def get_trades_by_portfolio(
    session: Session, portfolio_id: UUID, skip: int = 0, limit: int = 100
) -> List[Trade]:
    return list(
        session.execute(
            select(Trade)
            .where(Trade.portfolio_id == str(portfolio_id))
            .offset(skip)
            .limit(limit)
        )
        .scalars()
        .all()
    )


def create_trade(session: Session, trade_in: TradeCreate, portfolio_id: UUID) -> Trade:
    trade = Trade(**trade_in.model_dump(), portfolio_id=portfolio_id)
    session.add(trade)
    session.commit()
    session.refresh(trade)
    return trade


def update_trade(session: Session, trade: Trade, trade_in: TradeUpdate) -> Trade:
    trade_data = trade_in.model_dump(exclude_unset=True)
    for key, value in trade_data.items():
        setattr(trade, key, value)
    session.add(trade)
    session.commit()
    session.refresh(trade)
    return trade


def delete_trade(session: Session, trade: Trade) -> None:
    session.delete(trade)
    session.commit()
