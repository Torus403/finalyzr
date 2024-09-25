import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.portfolios import Portfolio


def get_portfolio_by_id(
    session: Session, portfolio_id: uuid.UUID
) -> Optional[Portfolio]:
    """
    Retrieve a portfolio by its unique id
    """
    return (
        session.execute(select(Portfolio).where(Portfolio.id == str(portfolio_id)))
        .scalars()
        .first()
    )


def get_portfolios_by_owner_id(
    session: Session, owner_id: uuid.UUID
) -> List[Portfolio]:
    """
    Get a list of portfolio's belonging to a user.
    """
    return list(
        session.execute(select(Portfolio).where(Portfolio.owner_id == str(owner_id)))
        .scalars()
        .all()
    )


def create_portfolio(session: Session, portfolio_data: dict) -> Portfolio:
    """
    Create a new portfolio in the database.
    """
    portfolio = Portfolio(**portfolio_data)
    session.add(portfolio)
    session.commit()
    session.refresh(portfolio)
    return portfolio


def update_portfolio(
    session: Session, portfolio: Portfolio, updates: dict
) -> Portfolio:
    """
    Updates an existing portfolio.
    """
    for key, value in updates.items():
        setattr(portfolio, key, value)
    session.add(portfolio)
    session.commit()
    session.refresh(portfolio)
    return portfolio


def delete_portfolio(session: Session, portfolio: Portfolio) -> None:
    """
    Deletes a portfolio from the database.
    """
    session.delete(portfolio)
    session.commit()
