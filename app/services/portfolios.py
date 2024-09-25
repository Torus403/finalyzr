import uuid

from sqlalchemy.orm import Session

from app.crud import portfolios as portfolio_crud
from app.models.portfolios import Portfolio
from app.schemas.portfolios import PortfolioCreate, PortfolioUpdate


def create_portfolio(
    session: Session, portfolio_in: PortfolioCreate, owner_id: uuid.UUID
) -> Portfolio:
    """
    Create a new portfolio.
    """
    portfolio_data = portfolio_in.model_dump()
    portfolio_data["owner_id"] = str(owner_id)
    return portfolio_crud.create_portfolio(session, portfolio_data)


def update_portfolio(
    session: Session, current_portfolio: Portfolio, new_portfolio: PortfolioUpdate
) -> Portfolio:
    """
    Update a portfolio.
    """
    update_data = new_portfolio.model_dump(exclude_unset=True)
    return portfolio_crud.update_portfolio(session, current_portfolio, update_data)
