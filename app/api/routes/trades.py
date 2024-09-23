import uuid
from typing import List

from fastapi import APIRouter, HTTPException, status, Path

from app.api.deps import SessionDep, CurrentUser
from app.crud.portfolios import get_portfolio_by_id
from app.crud.trades import (
    get_trade_by_id,
    get_trades_by_portfolio,
    create_trade,
    update_trade,
    delete_trade,
)
from app.schemas.login import Message
from app.schemas.trades import Trade, TradeCreate, TradeUpdate

router = APIRouter()


@router.post(
    "/",
    response_model=Trade,
    status_code=status.HTTP_201_CREATED,
)
def create_trade_endpoint(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    portfolio_id: uuid.UUID = Path(...),
    trade_in: TradeCreate,
):
    """
    Create a new trade within a portfolio.
    """
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
    trade = create_trade(session=session, trade_in=trade_in, portfolio_id=portfolio_id)
    return trade


@router.get("/", response_model=List[Trade])
def read_trades_by_portfolio(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    portfolio_id: uuid.UUID = Path(...),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve trades for a specific portfolio.
    """
    portfolio = get_portfolio_by_id(session=session, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    if portfolio.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view trades of this portfolio",
        )
    trades = get_trades_by_portfolio(
        session=session, portfolio_id=portfolio_id, skip=skip, limit=limit
    )
    return trades


@router.get("/{trade_id}", response_model=Trade)
def read_trade_by_id(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    portfolio_id: uuid.UUID = Path(...),
    trade_id: uuid.UUID,
):
    """
    Get a specific trade by ID within a given portfolio.
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

    trade = get_trade_by_id(session=session, trade_id=trade_id)
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trade not found"
        )
    if trade.portfolio_id != portfolio_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found in the specified portfolio",
        )

    return trade


@router.put("/{trade_id}", response_model=Trade)
def update_trade_endpoint(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    portfolio_id: uuid.UUID = Path(...),
    trade_id: uuid.UUID,
    trade_in: TradeUpdate,
):
    """
    Update an existing trade within a specific portfolio.
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

    trade = get_trade_by_id(session=session, trade_id=trade_id)
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trade not found"
        )
    if trade.portfolio_id != portfolio_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found in the specified portfolio",
        )

    updated_trade = update_trade(session=session, trade=trade, trade_in=trade_in)
    return updated_trade


@router.delete("/{trade_id}", response_model=dict)
def delete_trade_endpoint(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    portfolio_id: uuid.UUID = Path(...),
    trade_id: uuid.UUID,
):
    """
    Delete a trade within a specific portfolio.
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

    trade = get_trade_by_id(session=session, trade_id=trade_id)
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trade not found"
        )
    if trade.portfolio_id != portfolio_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found in the specified portfolio",
        )

    delete_trade(session=session, trade=trade)
    return Message(message="Trade deleted successfully")
