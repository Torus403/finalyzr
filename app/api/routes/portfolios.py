import uuid

from fastapi import APIRouter, HTTPException, status

import app.crud.portfolios as portfolio_crud
from app.api.deps import SessionDep, CurrentUser
from app.schemas.portfolios import (
    PortfolioPublic,
    PortfoliosPublic,
    PortfolioCreate,
    PortfolioUpdate,
)
from app.schemas.login import Message

router = APIRouter()


@router.post("/", response_model=PortfolioPublic)
def create_portfolio(
    *, session: SessionDep, current_user: CurrentUser, portfolio_in: PortfolioCreate
):
    """
    Create a new portfolio.
    """
    portfolio = portfolio_crud.create_portfolio(
        session=session, portfolio_in=portfolio_in, owner_id=current_user.id
    )
    return portfolio


@router.get("/")
def read_portfolios(
    *,
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Retrieve portfolios for the current user.
    """
    portfolios = portfolio_crud.get_portfolios_by_owner_id(
        session=session, owner_id=current_user.id
    )
    return PortfoliosPublic(data=portfolios)


@router.get("/{portfolio_id}", response_model=PortfolioPublic)
def read_portfolio(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    portfolio_id: uuid.UUID,
):
    """
    Get a specific portfolio by ID.
    """
    portfolio = portfolio_crud.get_portfolio_by_id(
        session=session, portfolio_id=portfolio_id
    )
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    if portfolio.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this portfolio",
        )
    return portfolio


@router.put("/{portfolio_id}", response_model=PortfolioPublic)
def update_portfolio(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    portfolio_id: uuid.UUID,
    portfolio_in: PortfolioUpdate,
):
    """
    Update an existing portfolio.
    """
    portfolio = portfolio_crud.get_portfolio_by_id(
        session=session, portfolio_id=portfolio_id
    )
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    if portfolio.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this portfolio",
        )
    updated_portfolio = portfolio_crud.update_portfolio(
        session=session, portfolio=portfolio, portfolio_in=portfolio_in
    )
    return updated_portfolio


@router.delete("/{portfolio_id}", response_model=Message)
def delete_portfolio(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    portfolio_id: uuid.UUID,
):
    """
    Delete a portfolio.
    """
    portfolio = portfolio_crud.get_portfolio_by_id(
        session=session, portfolio_id=portfolio_id
    )
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    if portfolio.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this portfolio",
        )
    portfolio_crud.delete_portfolio(session=session, portfolio=portfolio)
    return Message(message="Portfolio deleted successfully")
