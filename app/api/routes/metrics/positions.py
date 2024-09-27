import uuid
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status, Path, Query
from sqlalchemy.orm import Session

import app.crud.trades as trades_crud
from app.api.deps import SessionDep, CurrentUser
from app.crud.portfolios import get_portfolio_by_id
from app.models.trades import Trade, ActionType
from app.schemas.metrics import Position, HistoricalPosition
from app.utils import market_data

router = APIRouter()


def get_open_positions(session: Session, portfolio_id: uuid.UUID) -> List[Position]:
    trades = (
        session.query(Trade)
        .filter(Trade.portfolio_id == str(portfolio_id))
        .order_by(Trade.execution_timestamp)
        .all()
    )
    positions = {}
    for trade in trades:
        ticker = trade.ticker
        if ticker not in positions:
            positions[ticker] = {
                "quantity": Decimal(0),
                "entry_value": Decimal(0),
                "entry_quantity": Decimal(0),
                "entry_dates": [],
            }
        quantity = trade.quantity if trade.action == ActionType.BUY else -trade.quantity
        positions[ticker]["quantity"] += quantity
        if trade.action == ActionType.BUY:
            positions[ticker]["entry_value"] += trade.price * trade.quantity
            positions[ticker]["entry_quantity"] += trade.quantity
            positions[ticker]["entry_dates"].append(trade.execution_timestamp)

    position_list = []
    for ticker, data in positions.items():
        if data["quantity"] != 0:
            current_price = market_data.get_current_price(ticker)
            entry_price = (
                data["entry_value"] / data["entry_quantity"]
                if data["entry_quantity"] != 0
                else Decimal(0)
            )
            current_value = data["quantity"] * Decimal(current_price)
            unrealized_pl = (Decimal(current_price) - entry_price) * data["quantity"]
            position = Position(
                symbol=ticker,
                quantity=float(data["quantity"]),
                entry_price=float(entry_price),
                current_price=float(current_price),
                current_value=float(current_value),
                unrealized_pl=float(unrealized_pl),
                entry_date=min(data["entry_dates"]) if data["entry_dates"] else None,
            )
            position_list.append(position)
    return position_list


def get_historical_positions(
    session: Session,
    portfolio_id: uuid.UUID,
    order_by: str = "exit_date",
    sort: str = "desc",
    limit: int = 100,
) -> List[HistoricalPosition]:
    """
    Processes trades to identify closed positions and computes realized P/L.
    """
    buy_trades = trades_crud.get_buy_trades(session, portfolio_id)
    sell_trades = trades_crud.get_sell_trades(session, portfolio_id)

    historical_positions = []

    # Dictionary to track open positions per ticker
    open_positions = {}

    for buy in buy_trades:
        ticker = buy.ticker
        if ticker not in open_positions:
            open_positions[ticker] = []
        open_positions[ticker].append(
            {
                "trade_id": buy.id,
                "quantity": buy.quantity,
                "price": buy.price,
                "execution_timestamp": buy.execution_timestamp,
            }
        )

    for sell in sell_trades:
        ticker = sell.ticker
        if ticker not in open_positions or not open_positions[ticker]:
            # No corresponding buy trade; skip or handle as error
            continue

        sell_quantity = sell.quantity
        while sell_quantity > 0 and open_positions[ticker]:
            buy = open_positions[ticker][0]
            buy_quantity = buy["quantity"]

            if sell_quantity >= buy_quantity:
                # Entire buy trade is closed
                realized_quantity = buy_quantity
                sell_quantity -= buy_quantity
                open_positions[ticker].pop(0)
            else:
                # Partial closure of buy trade
                realized_quantity = sell_quantity
                buy["quantity"] -= sell_quantity
                sell_quantity = 0

            realized_pl = (sell.price - buy["price"]) * Decimal(realized_quantity)
            holding_period = (
                sell.execution_timestamp - buy["execution_timestamp"]
            ).days

            historical_position = HistoricalPosition(
                trade_id=sell.id,
                symbol=ticker,
                quantity=float(realized_quantity),
                entry_price=float(buy["price"]),
                exit_price=float(sell.price),
                realized_pl=float(realized_pl),
                entry_date=buy["execution_timestamp"],
                exit_date=sell.execution_timestamp,
                holding_period_days=holding_period,
            )
            historical_positions.append(historical_position)

    # Sorting
    reverse = True if sort.lower() == "desc" else False
    if hasattr(HistoricalPosition, order_by):
        historical_positions.sort(key=lambda x: getattr(x, order_by), reverse=reverse)

    # Limiting
    return historical_positions[:limit]


@router.get("/current", response_model=List[Position])
def get_current_positions(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    portfolio_id: uuid.UUID = Path(...),
):
    """Get all current open portfolio positions."""
    portfolio = get_portfolio_by_id(session=session, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    if portfolio.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add trades to this portfolio",
        )

    positions = get_open_positions(session=session, portfolio_id=portfolio_id)
    return positions


@router.get("/historic", response_model=List[HistoricalPosition])
def fetch_historical_positions(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    portfolio_id: uuid.UUID = Path(...),
    order_by: Optional[str] = Query("exit_date", description="Field to sort by"),
    sort: Optional[str] = Query("desc", description="asc or desc"),
    limit: Optional[int] = Query(100, description="Number of results to return"),
):
    portfolio = get_portfolio_by_id(session=session, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    if portfolio.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add trades to this portfolio",
        )

    historical_positions = get_historical_positions(
        session, portfolio_id, order_by, sort, limit
    )
    return historical_positions
