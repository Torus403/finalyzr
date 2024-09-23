from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.portfolios import Portfolio
from app.schemas.portfolios import PortfolioCreate, PortfolioUpdate


def get_portfolio_by_id(session: Session, portfolio_id: uuid.UUID) -> Optional[Portfolio]:
    return (
        session.execute(select(Portfolio).where(Portfolio.id == str(portfolio_id)))
        .scalars()
        .first()
    )


def get_portfolios_by_owner_id(
    session: Session, owner_id: uuid.UUID
) -> List[Portfolio]:
    return list(
        session.execute(
            select(Portfolio)
            .where(Portfolio.owner_id == str(owner_id))
        )
        .scalars()
        .all()
    )


def create_portfolio(
    session: Session, portfolio_in: PortfolioCreate, owner_id: uuid.UUID
) -> Portfolio:
    portfolio = Portfolio(
        name=portfolio_in.name, description=portfolio_in.description, owner_id=str(owner_id)
    )
    session.add(portfolio)
    session.commit()
    session.refresh(portfolio)
    return portfolio


def update_portfolio(
    session: Session, portfolio: Portfolio, portfolio_in: PortfolioUpdate
) -> Portfolio:
    portfolio_data = portfolio_in.model_dump(exclude_unset=True)
    for key, value in portfolio_data.items():
        setattr(portfolio, key, value)

    session.add(portfolio)
    session.commit()
    session.refresh(portfolio)
    return portfolio


def delete_portfolio(session: Session, portfolio: Portfolio) -> None:
    session.delete(portfolio)
    session.commit()
