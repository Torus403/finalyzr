from datetime import datetime

from sqlalchemy.orm import Session

from app.schemas.cash_actions import CashActionCreate, CashActionUpdate
from app.services.cash_actions import create_cash_action, update_cash_action


def test_create_cash_action_success(db: Session, create_portfolio_fixture):
    portfolio = create_portfolio_fixture()
    cash_action_create = CashActionCreate(
        action="deposit",
        amount=5000.0,
        execution_timestamp=datetime.utcnow(),
        currency="USD",
        notes="Initial deposit",
    )

    new_cash_action = create_cash_action(
        session=db, cash_action_in=cash_action_create, portfolio_id=portfolio.id
    )

    assert new_cash_action.id is not None
    assert new_cash_action.action == "deposit"
    assert new_cash_action.amount == 5000.0
    assert new_cash_action.portfolio_id == str(portfolio.id)
    assert new_cash_action.currency == "USD"


def test_update_cash_action_success(db: Session, create_cash_action_fixture):
    cash_action = create_cash_action_fixture(action="deposit", amount=1000.0)

    cash_action_update = CashActionUpdate(amount=1500.0, notes="Updated deposit amount")
    updated_cash_action = update_cash_action(
        session=db, current_cash_action=cash_action, new_cash_action=cash_action_update
    )

    assert updated_cash_action.amount == 1500.0
    assert updated_cash_action.notes == "Updated deposit amount"


def test_update_cash_action_partial(db: Session, create_cash_action_fixture):
    cash_action = create_cash_action_fixture(action="withdrawal", amount=2000.0)

    cash_action_update = CashActionUpdate(notes="Withdrawal adjustment")
    updated_cash_action = update_cash_action(
        session=db, current_cash_action=cash_action, new_cash_action=cash_action_update
    )

    assert updated_cash_action.amount == 2000.0  # Amount should remain the same
    assert updated_cash_action.notes == "Withdrawal adjustment"
