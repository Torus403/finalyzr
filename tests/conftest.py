import os
import uuid
from typing import List, Optional
from datetime import datetime
import pytest
import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.crud.users as user_crud
import app.crud.portfolios as portfolio_crud
from app.api.deps import get_db
from app.core.db import Base
from app.core.security import hash_password

# Need to import models to ensure they are registered on the metadata
from app.models.users import User
from app.models.portfolios import Portfolio
from app.models.trades import Trade, ActionType
from app.models.cash_actions import CashAction, CashActionType

from app.schemas.users import UserCreate
from app.schemas.portfolios import PortfolioCreate
from tests.utils.random_data import generate_random_email, generate_random_password

# Load environment variables as pytest runs in different env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite needs this
    poolclass=StaticPool,  # prevent multiple connections
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_engine():
    """
    Create a database engine for testing.
    Function-scoped, so runs for each function (prevents tests from using all same session)
    It creates all tables before tests and drops them after all tests have run.
    """
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db(db_engine):
    """
    Create a new database session for a test.
    This fixture is function-scoped, so it runs for each test function.
    It uses a nested transaction to isolate test data, rolling back after each test.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    session.begin_nested()

    @sqlalchemy.event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    yield session

    session.rollback()
    transaction.rollback()
    session.close()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    """
    Provide a test client for the FastAPI app.
    This fixture overrides the get_db dependency to use the test database session.
    """
    from app.main import app
    from fastapi.testclient import TestClient

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def create_user_fixture(db: Session):
    def _create_user(
        email: str = None, password: str = None, is_superuser: bool = False
    ) -> User:
        email = email or generate_random_email()
        password = password or generate_random_password()
        user_data = UserCreate(
            email=email, password=password, is_superuser=is_superuser
        ).model_dump()
        return user_crud.create_user(session=db, user_data=user_data)

    return _create_user


@pytest.fixture
def create_multiple_users_fixture(create_user_fixture):
    def _create_multiple_users(count: int) -> List[User]:
        return [create_user_fixture() for _ in range(count)]

    return _create_multiple_users


@pytest.fixture
def create_portfolio_fixture(db: Session, create_user_fixture):
    def _create_portfolio(
        name: Optional[str] = None,
        description: Optional[str] = None,
        owner_id: Optional[uuid.UUID] = None,
    ) -> Portfolio:
        if owner_id is None:
            user = create_user_fixture()
            owner_id = user.id

        name = name or "Test Portfolio"
        description = description or "This is a test portfolio."

        portfolio_data = PortfolioCreate(
            name=name,
            description=description,
        ).model_dump()
        portfolio_data["owner_id"] = str(owner_id)

        return portfolio_crud.create_portfolio(
            session=db, portfolio_data=portfolio_data
        )

    return _create_portfolio


@pytest.fixture
def create_multiple_portfolios_fixture(create_portfolio_fixture):
    def _create_multiple_portfolios(owner_id: uuid.UUID, count: int) -> List[Portfolio]:
        return [create_portfolio_fixture(owner_id=owner_id) for _ in range(count)]

    return _create_multiple_portfolios


@pytest.fixture
def create_trade_fixture(db: Session, create_portfolio_fixture):
    def _create_trade(
        portfolio_id: str = None,
        action: ActionType = ActionType.BUY,
        execution_timestamp: datetime = None,
        ticker: str = "AAPL",
        price: float = 150.0,
        quantity: float = 10.0,
        currency: str = "USD",
        notes: str = "Test trade",
    ) -> Trade:
        execution_timestamp = execution_timestamp or datetime.utcnow()

        if portfolio_id is None:
            portfolio = create_portfolio_fixture()
            portfolio_id = portfolio.id

        trade_data = {
            "portfolio_id": str(portfolio_id),
            "action": action,
            "execution_timestamp": execution_timestamp,
            "ticker": ticker,
            "price": price,
            "quantity": quantity,
            "currency": currency,
            "notes": notes,
        }
        trade = Trade(**trade_data)
        db.add(trade)
        db.commit()
        db.refresh(trade)
        return trade

    return _create_trade


@pytest.fixture
def create_cash_action_fixture(db: Session, create_portfolio_fixture):
    """Fixture to create a cash action for testing with customizable parameters."""

    def _create_cash_action(
        portfolio_id: str = None,
        action: CashActionType = CashActionType.DEPOSIT,
        amount: float = 1000.0,
        execution_timestamp: datetime = None,
        currency: str = "USD",
        notes: str = "Test cash action",
    ) -> CashAction:
        execution_timestamp = execution_timestamp or datetime.utcnow()

        if portfolio_id is None:
            portfolio = create_portfolio_fixture()
            portfolio_id = portfolio.id

        cash_action_data = {
            "portfolio_id": str(portfolio_id),
            "action": action,
            "amount": amount,
            "execution_timestamp": execution_timestamp,
            "currency": currency,
            "notes": notes,
        }
        cash_action = CashAction(**cash_action_data)
        db.add(cash_action)
        db.commit()
        db.refresh(cash_action)
        return cash_action

    return _create_cash_action
