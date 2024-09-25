import uuid

from sqlalchemy.orm import Session

from app.crud import cash_actions as cash_action_crud
from app.models.cash_actions import CashAction
from app.schemas.cash_actions import CashActionCreate, CashActionUpdate


def create_cash_action(
    session: Session, cash_action_in: CashActionCreate, portfolio_id: uuid.UUID
) -> CashAction:
    """
    Create a new cash action.
    """
    cash_action_data = cash_action_in.model_dump()
    cash_action_data["portfolio_id"] = str(portfolio_id)
    return cash_action_crud.create_cash_action(session, cash_action_data)


def update_cash_action(
    session: Session, current_cash_action: CashAction, new_cash_action: CashActionUpdate
) -> CashAction:
    """
    Update a cash action.
    """
    update_data = new_cash_action.model_dump(exclude_unset=True)
    return cash_action_crud.update_cash_action(
        session, current_cash_action, update_data
    )
