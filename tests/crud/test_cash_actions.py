import pytest
from sqlalchemy.orm import Session
from app.crud.cash_actions import (
    get_cash_action_by_id,
    get_cash_actions_by_portfolio,
    create_cash_action,
    update_cash_action,
    delete_cash_action
)
from app.models.cash_actions import CashAction, CashActionType
from datetime import datetime
import uuid


def test_create_cash_action_success(db: Session, create_cash_action_fixture):
    cash_action = create_cash_action_fixture()
    assert cash_action.id is not None
    assert cash_action.amount == 1000.0
    assert cash_action.currency == "USD"
    assert cash_action.action == CashActionType.DEPOSIT


def test_create_cash_action_with_custom_values(db: Session, create_cash_action_fixture):
    cash_action = create_cash_action_fixture(
        action=CashActionType.WITHDRAWAL, amount=500.0, currency="EUR"
    )
    assert cash_action.action == CashActionType.WITHDRAWAL
    assert cash_action.amount == 500.0
    assert cash_action.currency == "EUR"


def test_get_cash_action_by_id_exists(db: Session, create_cash_action_fixture):
    cash_action = create_cash_action_fixture()
    fetched_cash_action = get_cash_action_by_id(session=db, cash_action_id=uuid.UUID(cash_action.id))
    assert fetched_cash_action is not None
    assert fetched_cash_action.id == cash_action.id
    assert fetched_cash_action.amount == cash_action.amount


def test_get_cash_action_by_id_not_exists(db: Session):
    non_existent_id = uuid.uuid4()
    fetched_cash_action = get_cash_action_by_id(session=db, cash_action_id=non_existent_id)
    assert fetched_cash_action is None


def test_get_cash_actions_by_portfolio(db: Session, create_portfolio_fixture, create_cash_action_fixture):
    portfolio = create_portfolio_fixture()
    cash_actions = [create_cash_action_fixture(portfolio_id=str(portfolio.id)) for _ in range(3)]
    fetched_cash_actions = get_cash_actions_by_portfolio(session=db, portfolio_id=uuid.UUID(portfolio.id))
    assert len(fetched_cash_actions) == 3
    fetched_ids = {cash_action.id for cash_action in fetched_cash_actions}
    expected_ids = {cash_action.id for cash_action in cash_actions}
    assert fetched_ids == expected_ids


def test_update_cash_action_success(db: Session, create_cash_action_fixture):
    cash_action = create_cash_action_fixture()
    updates = {"amount": 2000.0}
    updated_cash_action = update_cash_action(session=db, cash_action=cash_action, updates=updates)
    assert updated_cash_action.amount == 2000.0


def test_delete_cash_action_success(db: Session, create_cash_action_fixture):
    cash_action = create_cash_action_fixture()
    delete_cash_action(session=db, cash_action=cash_action)
    fetched_cash_action = get_cash_action_by_id(session=db, cash_action_id=uuid.UUID(cash_action.id))
    assert fetched_cash_action is None
