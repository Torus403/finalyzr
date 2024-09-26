from sqlalchemy.orm import Session

from app.schemas.portfolios import PortfolioCreate, PortfolioUpdate
from app.services.portfolios import create_portfolio, update_portfolio


def test_create_portfolio_success(db: Session, create_user_fixture):
    user = create_user_fixture()
    portfolio_create = PortfolioCreate(
        name="My Portfolio", description="My first portfolio"
    )
    new_portfolio = create_portfolio(
        session=db, portfolio_in=portfolio_create, owner_id=user.id
    )

    assert new_portfolio.id is not None
    assert new_portfolio.name == "My Portfolio"
    assert new_portfolio.description == "My first portfolio"
    assert new_portfolio.owner_id == str(user.id)


def test_update_portfolio_success(db: Session, create_portfolio_fixture):
    portfolio = create_portfolio_fixture(
        name="Initial Portfolio", description="Initial Description"
    )

    portfolio_update = PortfolioUpdate(name="Updated Portfolio")
    updated_portfolio = update_portfolio(
        session=db, current_portfolio=portfolio, new_portfolio=portfolio_update
    )

    assert updated_portfolio.name == "Updated Portfolio"
    assert (
        updated_portfolio.description == "Initial Description"
    )  # Since description is not updated


def test_update_portfolio_partial(db: Session, create_portfolio_fixture):
    portfolio = create_portfolio_fixture(
        name="Another Portfolio", description="Another Description"
    )

    portfolio_update = PortfolioUpdate(description="Updated Description")
    updated_portfolio = update_portfolio(
        session=db, current_portfolio=portfolio, new_portfolio=portfolio_update
    )

    assert updated_portfolio.name == "Another Portfolio"  # Name should remain the same
    assert updated_portfolio.description == "Updated Description"
