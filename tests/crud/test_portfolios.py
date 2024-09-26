import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.portfolios import (
    create_portfolio,
    get_portfolio_by_id,
    get_portfolios_by_owner_id,
    update_portfolio,
    delete_portfolio,
)
from app.models.portfolios import Portfolio


def test_create_portfolio_success(db: Session, create_portfolio_fixture):
    portfolio = create_portfolio_fixture()
    assert portfolio.id is not None
    assert portfolio.owner_id is not None
    assert portfolio.name is not None
    assert portfolio.description is not None


def test_create_portfolio_duplicate_id(db: Session, create_portfolio_fixture):
    portfolio = create_portfolio_fixture()
    duplicate_data = {
        "id": portfolio.id,
        "owner_id": portfolio.owner_id,
        "name": "Duplicate Portfolio",
        "description": "Another description",
    }
    with pytest.raises(IntegrityError):
        create_portfolio(session=db, portfolio_data=duplicate_data)


def test_get_portfolio_by_id_exists(db: Session, create_portfolio_fixture):
    portfolio = create_portfolio_fixture()
    fetched_portfolio = get_portfolio_by_id(
        session=db, portfolio_id=uuid.UUID(portfolio.id)
    )
    assert fetched_portfolio is not None
    assert fetched_portfolio.id == portfolio.id
    assert fetched_portfolio.owner_id == portfolio.owner_id


def test_get_portfolio_by_id_not_exists(db: Session):
    non_existent_id = uuid.uuid4()
    fetched_portfolio = get_portfolio_by_id(session=db, portfolio_id=non_existent_id)
    assert fetched_portfolio is None


def test_get_portfolios_by_owner_id(
    db: Session, create_portfolio_fixture, create_user_fixture
):
    user = create_user_fixture()
    portfolios = [create_portfolio_fixture(owner_id=user.id) for _ in range(3)]
    fetched_portfolios = get_portfolios_by_owner_id(session=db, owner_id=user.id)
    assert len(fetched_portfolios) == 3
    fetched_ids = {portfolio.id for portfolio in fetched_portfolios}
    expected_ids = {portfolio.id for portfolio in portfolios}
    assert fetched_ids == expected_ids


def test_update_portfolio_success(db: Session, create_portfolio_fixture):
    portfolio = create_portfolio_fixture()
    updates = {"name": "Updated Portfolio Name"}
    updated_portfolio = update_portfolio(
        session=db, portfolio=portfolio, updates=updates
    )
    assert updated_portfolio.name == "Updated Portfolio Name"


def test_update_portfolio_partial(db: Session, create_portfolio_fixture):
    portfolio = create_portfolio_fixture()
    original_name = portfolio.name
    updates = {
        "description": "Updated Description"
    }
    updated_portfolio = update_portfolio(
        session=db, portfolio=portfolio, updates=updates
    )
    assert updated_portfolio.name == original_name
    assert updated_portfolio.description == "Updated Description"


def test_delete_portfolio_success(db: Session, create_portfolio_fixture):
    portfolio = create_portfolio_fixture()
    delete_portfolio(session=db, portfolio=portfolio)
    fetched_portfolio = get_portfolio_by_id(
        session=db, portfolio_id=uuid.UUID(portfolio.id)
    )
    assert fetched_portfolio is None


def test_delete_portfolio_not_in_db(db: Session):
    non_existent_portfolio = Portfolio(
        id=str(uuid.uuid4()),
        owner_id=str(uuid.uuid4()),
        name="Non-existent Portfolio",
        description=None,
    )
    with pytest.raises(Exception):
        delete_portfolio(session=db, portfolio=non_existent_portfolio)


def test_get_portfolios_by_owner_id_empty(db: Session, create_user_fixture):
    user = create_user_fixture()
    portfolios = get_portfolios_by_owner_id(session=db, owner_id=user.id)
    assert len(portfolios) == 0
