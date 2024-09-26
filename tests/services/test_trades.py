from datetime import datetime

from sqlalchemy.orm import Session

from app.schemas.trades import TradeCreate, TradeUpdate
from app.services.trades import create_trade, update_trade


def test_create_trade_success(db: Session, create_portfolio_fixture):
    portfolio = create_portfolio_fixture()
    trade_create = TradeCreate(
        action="buy",
        execution_timestamp=datetime.utcnow(),
        ticker="GOOGL",
        price=2500.0,
        quantity=5.0,
        currency="USD",
        notes="Buy Google stock",
    )

    new_trade = create_trade(
        session=db, trade_in=trade_create, portfolio_id=portfolio.id
    )

    assert new_trade.id is not None
    assert new_trade.action == "buy"
    assert new_trade.ticker == "GOOGL"
    assert new_trade.price == 2500.0
    assert new_trade.quantity == 5.0
    assert new_trade.portfolio_id == str(portfolio.id)


def test_update_trade_success(db: Session, create_trade_fixture):
    trade = create_trade_fixture(
        action="buy", ticker="AAPL", price=150.0, quantity=10.0
    )

    trade_update = TradeUpdate(ticker="MSFT", price=300.0)
    updated_trade = update_trade(
        session=db, current_trade=trade, new_trade=trade_update
    )

    assert updated_trade.ticker == "MSFT"
    assert updated_trade.price == 300.0
    assert updated_trade.quantity == 10.0  # Quantity should remain the same


def test_update_trade_partial(db: Session, create_trade_fixture):
    trade = create_trade_fixture(
        action="sell", ticker="TSLA", price=800.0, quantity=20.0
    )

    trade_update = TradeUpdate(quantity=25.0)
    updated_trade = update_trade(
        session=db, current_trade=trade, new_trade=trade_update
    )

    assert updated_trade.ticker == "TSLA"  # Ticker should remain unchanged
    assert updated_trade.quantity == 25.0
    assert updated_trade.price == 800.0  # Price should remain unchanged
