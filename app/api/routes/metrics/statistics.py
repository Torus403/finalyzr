import uuid

from fastapi import APIRouter, HTTPException, status, Path, Query
from sqlalchemy.orm import Session

import app.crud.trades as trades_crud
from app.api.deps import SessionDep, CurrentUser
from app.crud.portfolios import get_portfolio_by_id
from app.models.trades import ActionType
from app.schemas.metrics import TradeMetrics, Period
from app.utils.time import get_date_range

router = APIRouter()


def calculate_trade_metrics(
    session: Session, portfolio_id: uuid.UUID, period: Period
) -> TradeMetrics:
    try:
        start_date, end_date = get_date_range(period)
    except ValueError as e:
        raise e

    trades = trades_crud.get_trades_within_period(
        session, portfolio_id, start_date, end_date
    )

    if not trades:
        return TradeMetrics(
            average_trade_volume=0,
            trade_frequency_days_per_trade=None,
            trade_frequency_trades_per_day=0,
            average_holding_period_days=None,
            win_loss_ratio=None,  # Set to None instead of 0
        )

    # Average Trade Volume
    total_volume = sum(float(trade.quantity) for trade in trades)
    average_trade_volume = total_volume / len(trades)

    # Trade Frequency
    if len(trades) < 2:
        trade_frequency_days_per_trade = None  # Undefined
    else:
        # Calculate average days between consecutive trades
        sorted_trades = sorted(trades, key=lambda x: x.execution_timestamp)
        deltas = [
            (
                sorted_trades[i + 1].execution_timestamp
                - sorted_trades[i].execution_timestamp
            ).days
            for i in range(len(sorted_trades) - 1)
        ]
        trade_frequency_days_per_trade = sum(deltas) / len(deltas)

    # Trades per day
    total_days = (end_date - start_date).days or 1  # Avoid division by zero
    trade_frequency_trades_per_day = len(trades) / total_days

    # Average Holding Period
    # Need to pair buy and sell trades to calculate holding periods
    buy_trades = [trade for trade in trades if trade.action == ActionType.BUY]
    sell_trades = [trade for trade in trades if trade.action == ActionType.SELL]

    # Simple FIFO matching
    buy_trades_sorted = sorted(buy_trades, key=lambda x: x.execution_timestamp)
    sell_trades_sorted = sorted(sell_trades, key=lambda x: x.execution_timestamp)

    holding_periods = []
    buy_queue = buy_trades_sorted.copy()

    for sell in sell_trades_sorted:
        sell_quantity = sell.quantity
        while sell_quantity > 0 and buy_queue:
            buy = buy_queue[0]
            if buy.quantity <= sell_quantity:
                holding_days = (sell.execution_timestamp - buy.execution_timestamp).days
                holding_periods.append(holding_days)
                sell_quantity -= buy.quantity
                buy_queue.pop(0)
            else:
                holding_days = (sell.execution_timestamp - buy.execution_timestamp).days
                holding_periods.append(holding_days)
                buy.quantity -= sell_quantity
                sell_quantity = 0

    if holding_periods:
        average_holding_period_days = sum(holding_periods) / len(holding_periods)
    else:
        average_holding_period_days = None

    # Win/Loss Ratio
    # Assuming a trade is a win if sell price > buy price, else loss
    wins = 0
    losses = 0
    buy_queue = buy_trades_sorted.copy()

    for sell in sell_trades_sorted:
        sell_quantity = sell.quantity
        while sell_quantity > 0 and buy_queue:
            buy = buy_queue[0]
            if buy.quantity <= sell_quantity:
                pl = float(sell.price - buy.price) * float(buy.quantity)
                if pl > 0:
                    wins += 1
                elif pl < 0:
                    losses += 1
                sell_quantity -= buy.quantity
                buy_queue.pop(0)
            else:
                pl = float(sell.price - buy.price) * float(sell_quantity)
                if pl > 0:
                    wins += 1
                elif pl < 0:
                    losses += 1
                buy.quantity -= sell_quantity
                sell_quantity = 0

    if losses == 0:
        win_loss_ratio = None if wins > 0 else 0  # Set to None instead of inf
    else:
        win_loss_ratio = wins / losses

    return TradeMetrics(
        average_trade_volume=average_trade_volume,
        trade_frequency_days_per_trade=trade_frequency_days_per_trade,
        trade_frequency_trades_per_day=trade_frequency_trades_per_day,
        average_holding_period_days=average_holding_period_days,
        win_loss_ratio=win_loss_ratio,
    )


@router.get("/", response_model=TradeMetrics)
def get_trade_metrics(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    portfolio_id: uuid.UUID = Path(...),
    period: Period = Query(
        Period.ALL,
        description="Period for metrics (e.g., '1D', '1W', '1M', '3M', '6M', '1Y', '3Y', '5Y', '10Y', 'YTD', 'All')",
    )
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

    metrics = calculate_trade_metrics(session, portfolio_id, period)
    return metrics
