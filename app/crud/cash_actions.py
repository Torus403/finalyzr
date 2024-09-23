from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.cash_actions import CashAction
from app.schemas.cash_actions import CashActionCreate, CashActionUpdate


def get_cash_action_by_id(
    session: Session, cash_action_id: UUID
) -> Optional[CashAction]:
    return (
        session.execute(select(CashAction).where(CashAction.id == str(cash_action_id)))
        .scalars()
        .first()
    )


def get_cash_actions_by_portfolio(
    session: Session, portfolio_id: UUID, skip: int = 0, limit: int = 100
) -> List[CashAction]:
    return list(
        session.execute(
            select(CashAction)
            .where(CashAction.portfolio_id == str(portfolio_id))
            .offset(skip)
            .limit(limit)
        )
        .scalars()
        .all()
    )


def create_cash_action(
    session: Session, cash_action_in: CashActionCreate, portfolio_id: UUID
) -> CashAction:
    cash_action = CashAction(**cash_action_in.model_dump(), portfolio_id=portfolio_id)
    session.add(cash_action)
    session.commit()
    session.refresh(cash_action)
    return cash_action


def update_cash_action(
    session: Session, cash_action: CashAction, cash_action_in: CashActionUpdate
) -> CashAction:
    cash_action_data = cash_action_in.model_dump(exclude_unset=True)
    for key, value in cash_action_data.items():
        setattr(cash_action, key, value)
    session.add(cash_action)
    session.commit()
    session.refresh(cash_action)
    return cash_action


def delete_cash_action(session: Session, cash_action: CashAction) -> None:
    session.delete(cash_action)
    session.commit()
