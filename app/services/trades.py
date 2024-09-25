import uuid

from sqlalchemy.orm import Session

from app.crud import trades as trade_crud
from app.models.trades import Trade
from app.schemas.trades import TradeCreate, TradeUpdate


def create_trade(session: Session, trade_in: TradeCreate, portfolio_id: uuid.UUID) -> Trade:
    """
    Create a new trade.
    """
    trade_data = trade_in.model_dump()
    trade_data["portfolio_id"] = str(portfolio_id)
    return trade_crud.create_trade(session, trade_data)


def update_trade(
    session: Session, current_trade: Trade, new_trade: TradeUpdate
) -> Trade:
    """
    Update a trade.
    """
    update_data = new_trade.model_dump(exclude_unset=True)
    return trade_crud.update_trade(session, current_trade, update_data)
