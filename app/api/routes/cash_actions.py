import uuid
from typing import List

from fastapi import APIRouter, HTTPException, status, Path

from app.api.deps import SessionDep, CurrentUser
from app.crud.portfolios import get_portfolio_by_id
from app.schemas.login import Message
from app.schemas.cash_actions import CashAction, CashActionCreate, CashActionUpdate
from app.crud.cash_actions import (
    get_cash_action_by_id,
    get_cash_actions_by_portfolio,
    create_cash_action,
    update_cash_action,
    delete_cash_action
)


router = APIRouter()


@router.post(
    "/",
    response_model=CashAction,
    status_code=status.HTTP_201_CREATED,
)
def create_cash_action_endpoint(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    portfolio_id: uuid.UUID = Path(...),
    cash_action_in: CashActionCreate
):
    """
    Create a new cash action within a portfolio.
    """
    portfolio = get_portfolio_by_id(session=session, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    if portfolio.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add cash actions to this portfolio",
        )
    cash_action = create_cash_action(session=session, cash_action_in=cash_action_in, portfolio_id=portfolio_id)
    return cash_action


@router.get("/", response_model=List[CashAction])
def read_cash_actions_by_portfolio(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    portfolio_id: uuid.UUID = Path(...),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve cash actions for a specific portfolio.
    """
    portfolio = get_portfolio_by_id(session=session, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    if portfolio.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view cash actions of this portfolio",
        )
    cash_actions = get_cash_actions_by_portfolio(
        session=session, portfolio_id=portfolio_id, skip=skip, limit=limit
    )
    return cash_actions


@router.get("/{cash_action_id}", response_model=CashAction)
def read_cash_action_by_id(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    portfolio_id: uuid.UUID = Path(...),
    cash_action_id: uuid.UUID,
):
    """
    Get a specific cash action by ID within a given portfolio.
    """
    portfolio = get_portfolio_by_id(session=session, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    if portfolio.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this portfolio",
        )

    cash_action = get_cash_action_by_id(session=session, cash_action_id=cash_action_id)
    if not cash_action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cash action not found"
        )
    if cash_action.portfolio_id != portfolio_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cash action not found in the specified portfolio"
        )

    return cash_action


@router.put("/{cash_action_id}", response_model=CashAction)
def update_cash_action_endpoint(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    portfolio_id: uuid.UUID = Path(...),
    cash_action_id: uuid.UUID,
    cash_action_in: CashActionUpdate,
):
    """
    Update an existing cash action within a specific portfolio.
    """
    portfolio = get_portfolio_by_id(session=session, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    if portfolio.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this portfolio",
        )

    cash_action = get_cash_action_by_id(session=session, cash_action_id=cash_action_id)
    if not cash_action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cash action not found"
        )
    if cash_action.portfolio_id != portfolio_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cash action not found in the specified portfolio"
        )

    updated_cash_action = update_cash_action(session=session, cash_action=cash_action, cash_action_in=cash_action_in)
    return updated_cash_action


@router.delete("/{cash_action_id}", response_model=dict)
def delete_cash_action_endpoint(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    portfolio_id: uuid.UUID = Path(...),
    cash_action_id: uuid.UUID,
):
    """
    Delete a cash action within a specific portfolio.
    """
    portfolio = get_portfolio_by_id(session=session, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    if portfolio.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this portfolio",
        )

    cash_action = get_cash_action_by_id(session=session, cash_action_id=cash_action_id)
    if not cash_action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cash action not found"
        )
    if cash_action.portfolio_id != portfolio_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cash action not found in the specified portfolio"
        )

    delete_cash_action(session=session, cash_action=cash_action)
    return Message(message="Cash action deleted successfully")
