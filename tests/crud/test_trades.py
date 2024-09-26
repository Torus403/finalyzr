import uuid
import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from app.crud.trades import (
    get_trade_by_id,
    get_trades_by_portfolio,
    create_trade,
    update_trade,
    delete_trade,
)
from app.models.trades import Trade, ActionType


def test_create_trade_success(db: Session, create_portfolio_fixture):
    portfolio = create_portfolio_fixture()
    trade_data = {
        "portfolio_id": str(portfolio.id),
        "action": ActionType.BUY,
        "execution_timestamp": datetime.utcnow(),
        "ticker": "AAPL",
        "price": 150.0,
        "quantity": 10.0,
        "currency": "USD",
        "notes": "Test trade",
    }
    trade = create_trade(session=db, trade_data=trade_data)
    assert trade.id is not None
    assert trade.portfolio_id == str(portfolio.id)
    assert trade.action == ActionType.BUY
    assert trade.ticker == "AAPL"
    assert trade.price == 150.0
    assert trade.quantity == 10.0


def test_get_trade_by_id_exists(db: Session, create_trade_fixture):
    trade = create_trade_fixture()
    fetched_trade = get_trade_by_id(session=db, trade_id=uuid.UUID(trade.id))
    assert fetched_trade is not None
    assert fetched_trade.id == trade.id
    assert fetched_trade.ticker == trade.ticker


def test_get_trade_by_id_not_exists(db: Session):
    non_existent_id = uuid.uuid4()
    fetched_trade = get_trade_by_id(session=db, trade_id=non_existent_id)
    assert fetched_trade is None


def test_get_trades_by_portfolio(db: Session, create_portfolio_fixture, create_trade_fixture):
    portfolio = create_portfolio_fixture()
    trades = [create_trade_fixture(portfolio_id=str(portfolio.id)) for _ in range(3)]
    fetched_trades = get_trades_by_portfolio(session=db, portfolio_id=uuid.UUID(portfolio.id))
    assert len(fetched_trades) == 3
    fetched_ids = {trade.id for trade in fetched_trades}
    expected_ids = {trade.id for trade in trades}
    assert fetched_ids == expected_ids


def test_update_trade_success(db: Session, create_trade_fixture):
    trade = create_trade_fixture()
    updates = {"ticker": "MSFT"}
    updated_trade = update_trade(session=db, trade=trade, updates=updates)
    assert updated_trade.ticker == "MSFT"


def test_update_trade_partial(db: Session, create_trade_fixture):
    trade = create_trade_fixture()
    original_ticker = trade.ticker
    updates = {"price": 200.0}
    updated_trade = update_trade(session=db, trade=trade, updates=updates)
    assert updated_trade.ticker == original_ticker
    assert updated_trade.price == 200.0


def test_delete_trade_success(db: Session, create_trade_fixture):
    trade = create_trade_fixture()
    delete_trade(session=db, trade=trade)
    fetched_trade = get_trade_by_id(session=db, trade_id=uuid.UUID(trade.id))
    assert fetched_trade is None


def test_delete_trade_not_in_db(db: Session):
    non_existent_trade = Trade(
        id=str(uuid.uuid4()),
        portfolio_id=str(uuid.uuid4()),
        action=ActionType.BUY,
        execution_timestamp=datetime.utcnow(),
        ticker="Non-existent Trade",
        price=100.0,
        quantity=10.0,
        currency="USD",
    )
    with pytest.raises(Exception):
        delete_trade(session=db, trade=non_existent_trade)


def test_get_trades_by_portfolio_empty(db: Session, create_portfolio_fixture):
    portfolio = create_portfolio_fixture()
    trades = get_trades_by_portfolio(session=db, portfolio_id=uuid.UUID(portfolio.id))
    assert len(trades) == 0
