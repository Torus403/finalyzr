import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.cash_actions import CashAction
from app.schemas.cash_actions import CashActionCreate, CashActionUpdate


def get_cash_action_by_id(
    session: Session, cash_action_id: uuid.UUID
) -> Optional[CashAction]:
    """Retrieve a cash action by its ID."""
    return session.get(CashAction, str(cash_action_id))


def get_cash_actions_by_portfolio(
    session: Session, portfolio_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> List[CashAction]:
    """Retrieve all cash actions for a portfolio with pagination."""
    stmt = (
        select(CashAction)
        .where(CashAction.portfolio_id == str(portfolio_id))
        .offset(skip)
        .limit(limit)
    )
    return list(session.execute(stmt).scalars().all())


def create_cash_action(session: Session, cash_action_data: dict) -> CashAction:
    """Create a new cash action in the database."""
    cash_action = CashAction(**cash_action_data)
    session.add(cash_action)
    session.commit()
    session.refresh(cash_action)
    return cash_action


def update_cash_action(
    session: Session, cash_action: CashAction, updates: dict
) -> CashAction:
    """Update an existing cash action."""
    for key, value in updates.items():
        setattr(cash_action, key, value)
    session.add(cash_action)
    session.commit()
    session.refresh(cash_action)
    return cash_action


def delete_cash_action(session: Session, cash_action: CashAction) -> None:
    """Delete a cash action from the database"""
    session.delete(cash_action)
    session.commit()
