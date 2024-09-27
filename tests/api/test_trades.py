import uuid
from datetime import timedelta

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import create_access_token


def authenticate_user(client: TestClient, user):
    """Helper function to authenticate and return headers."""
    access_token = create_access_token(
        user.id, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"Authorization": f"Bearer {access_token}"}


def test_create_trade_success(
    client: TestClient, create_user_fixture, create_portfolio_fixture
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)

    trade_data = {
        "action": "buy",
        "execution_timestamp": "2024-01-01T12:00:00Z",
        "ticker": "AAPL",
        "price": 150.0,
        "quantity": 10.0,
        "currency": "USD",
        "notes": "Initial trade",
    }

    response = client.post(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}/trades/",
        json=trade_data,
        headers=headers,
    )

    assert response.status_code == 201
    json_response = response.json()
    assert json_response["ticker"] == trade_data["ticker"]
    assert json_response["action"] == trade_data["action"]
    assert json_response["portfolio_id"] == str(portfolio.id)


def test_create_trade_portfolio_not_found(client: TestClient, create_user_fixture):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    non_existent_portfolio_id = str(uuid.uuid4())

    trade_data = {
        "action": "buy",
        "execution_timestamp": "2024-01-01T12:00:00Z",
        "ticker": "AAPL",
        "price": 150.0,
        "quantity": 10.0,
        "currency": "USD",
        "notes": "Initial trade",
    }

    response = client.post(
        f"{settings.API_V1_STR}/portfolios/{non_existent_portfolio_id}/trades/",
        json=trade_data,
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Portfolio not found"


def test_read_trades_by_portfolio_success(
    client: TestClient,
    create_user_fixture,
    create_portfolio_fixture,
    create_trade_fixture,
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)

    create_trade_fixture(portfolio_id=portfolio.id)
    create_trade_fixture(portfolio_id=portfolio.id)

    response = client.get(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}/trades/", headers=headers
    )

    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == 2


def test_read_trade_by_id_success(
    client: TestClient,
    create_user_fixture,
    create_portfolio_fixture,
    create_trade_fixture,
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)
    trade = create_trade_fixture(portfolio_id=portfolio.id)

    response = client.get(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}/trades/{trade.id}",
        headers=headers,
    )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["id"] == str(trade.id)
    assert json_response["ticker"] == trade.ticker
    assert json_response["portfolio_id"] == str(portfolio.id)


def test_read_trade_by_id_not_found(
    client: TestClient, create_user_fixture, create_portfolio_fixture
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)
    non_existent_trade_id = str(uuid.uuid4())

    response = client.get(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}/trades/{non_existent_trade_id}",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Trade not found"


def test_update_trade_success(
    client: TestClient,
    create_user_fixture,
    create_portfolio_fixture,
    create_trade_fixture,
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)
    trade = create_trade_fixture(portfolio_id=portfolio.id)

    update_data = {
        "action": "sell",
        "execution_timestamp": "2024-01-02T12:00:00Z",
        "ticker": "AAPL",
        "price": 155.0,
        "quantity": 5.0,
        "currency": "USD",
        "notes": "Updated trade",
    }

    response = client.put(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}/trades/{trade.id}",
        json=update_data,
        headers=headers,
    )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["action"] == update_data["action"]
    assert json_response["ticker"] == update_data["ticker"]
    assert float(json_response["price"]) == update_data["price"]


def test_update_trade_not_found(
    client: TestClient, create_user_fixture, create_portfolio_fixture
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)
    non_existent_trade_id = str(uuid.uuid4())

    update_data = {
        "action": "sell",
        "execution_timestamp": "2024-01-02T12:00:00Z",
        "ticker": "AAPL",
        "price": 155.0,
        "quantity": 5.0,
        "currency": "USD",
        "notes": "Updated trade",
    }

    response = client.put(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}/trades/{non_existent_trade_id}",
        json=update_data,
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Trade not found"


def test_delete_trade_success(
    client: TestClient,
    create_user_fixture,
    create_portfolio_fixture,
    create_trade_fixture,
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)
    trade = create_trade_fixture(portfolio_id=portfolio.id)

    response = client.delete(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}/trades/{trade.id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Trade deleted successfully"


def test_delete_trade_not_found(
    client: TestClient, create_user_fixture, create_portfolio_fixture
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)
    non_existent_trade_id = str(uuid.uuid4())

    response = client.delete(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}/trades/{non_existent_trade_id}",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Trade not found"
