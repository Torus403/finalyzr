import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, status, Path
from sqlalchemy.orm import Session

from app.api.deps import SessionDep, CurrentUser
from app.api.routes.metrics.positions import get_open_positions
from app.crud.portfolios import get_portfolio_by_id
from app.schemas.metrics import PortfolioOverview
from app.services.cash_actions import calculate_cash_balance

router = APIRouter()


def calculate_portfolio_overview(
    session: Session, portfolio_id: uuid.UUID
) -> PortfolioOverview:
    cash_balance = calculate_cash_balance(session=session, portfolio_id=portfolio_id)
    positions = get_open_positions(session=session, portfolio_id=portfolio_id)
    total_open_positions_value = sum(position.current_value for position in positions)
    cost_basis = sum(position.entry_price * position.quantity for position in positions)
    unrealized_returns_absolute = total_open_positions_value - cost_basis
    unrealized_returns_percentage = (
        (unrealized_returns_absolute / cost_basis) * 100 if cost_basis != 0 else 0
    )
    total_portfolio_value = cash_balance + total_open_positions_value
    number_of_open_positions = len(positions)

    overview = PortfolioOverview(
        total_portfolio_value=total_portfolio_value,
        cash_balance=cash_balance,
        total_open_positions_value=total_open_positions_value,
        unrealized_returns_percentage=unrealized_returns_percentage,
        unrealized_returns_absolute=unrealized_returns_absolute,
        number_of_open_positions=number_of_open_positions,
    )
    return overview


@router.get("/current", response_model=PortfolioOverview)
def get_current_portfolio_overview(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    portfolio_id: uuid.UUID = Path(...),
) -> Any:
    """Get overview of all current open portfolio positions."""
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

    overview = calculate_portfolio_overview(session=session, portfolio_id=portfolio_id)
    return overview
