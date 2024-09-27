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


def test_create_cash_action_success(
    client: TestClient, create_user_fixture, create_portfolio_fixture
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)

    cash_action_data = {
        "action": "deposit",
        "amount": 1000.0,
        "execution_timestamp": "2024-01-01T12:00:00Z",
        "currency": "USD",
        "notes": "Initial deposit",
    }

    response = client.post(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}/cash_actions/",
        json=cash_action_data,
        headers=headers,
    )

    assert response.status_code == 201
    json_response = response.json()
    assert json_response["action"] == cash_action_data["action"]
    assert float(json_response["amount"]) == cash_action_data["amount"]
    assert json_response["portfolio_id"] == str(portfolio.id)


def test_create_cash_action_portfolio_not_found(
    client: TestClient, create_user_fixture
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    non_existent_portfolio_id = str(uuid.uuid4())

    cash_action_data = {
        "action": "deposit",
        "amount": 1000.0,
        "execution_timestamp": "2024-01-01T12:00:00Z",
        "currency": "USD",
        "notes": "Initial deposit",
    }

    response = client.post(
        f"{settings.API_V1_STR}/portfolios/{non_existent_portfolio_id}/cash_actions/",
        json=cash_action_data,
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Portfolio not found"


def test_read_cash_actions_by_portfolio_success(
    client: TestClient,
    create_user_fixture,
    create_portfolio_fixture,
    create_cash_action_fixture,
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)

    create_cash_action_fixture(portfolio_id=portfolio.id)
    create_cash_action_fixture(portfolio_id=portfolio.id)

    response = client.get(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}/cash_actions/",
        headers=headers,
    )

    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == 2


def test_read_cash_action_by_id_success(
    client: TestClient,
    create_user_fixture,
    create_portfolio_fixture,
    create_cash_action_fixture,
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)
    cash_action = create_cash_action_fixture(portfolio_id=portfolio.id)

    response = client.get(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}/cash_actions/{cash_action.id}",
        headers=headers,
    )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["id"] == str(cash_action.id)
    assert json_response["amount"] == str(cash_action.amount)
    assert json_response["portfolio_id"] == str(portfolio.id)


def test_read_cash_action_by_id_not_found(
    client: TestClient, create_user_fixture, create_portfolio_fixture
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)
    non_existent_cash_action_id = str(uuid.uuid4())

    response = client.get(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}/cash_actions/{non_existent_cash_action_id}",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Cash action not found"


def test_update_cash_action_success(
    client: TestClient,
    create_user_fixture,
    create_portfolio_fixture,
    create_cash_action_fixture,
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)
    cash_action = create_cash_action_fixture(portfolio_id=portfolio.id)

    update_data = {
        "action": "withdrawal",
        "amount": 500.0,
        "execution_timestamp": "2024-01-02T12:00:00Z",
        "currency": "USD",
        "notes": "Updated cash action",
    }

    response = client.put(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}/cash_actions/{cash_action.id}",
        json=update_data,
        headers=headers,
    )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["action"] == update_data["action"]
    assert float(json_response["amount"]) == update_data["amount"]


def test_update_cash_action_not_found(
    client: TestClient, create_user_fixture, create_portfolio_fixture
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)
    non_existent_cash_action_id = str(uuid.uuid4())

    update_data = {
        "action": "withdrawal",
        "amount": 500.0,
        "execution_timestamp": "2024-01-02T12:00:00Z",
        "currency": "USD",
        "notes": "Updated cash action",
    }

    response = client.put(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}/cash_actions/{non_existent_cash_action_id}",
        json=update_data,
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Cash action not found"


def test_delete_cash_action_success(
    client: TestClient,
    create_user_fixture,
    create_portfolio_fixture,
    create_cash_action_fixture,
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)
    cash_action = create_cash_action_fixture(portfolio_id=portfolio.id)

    response = client.delete(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}/cash_actions/{cash_action.id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Cash action deleted successfully"


def test_delete_cash_action_not_found(
    client: TestClient, create_user_fixture, create_portfolio_fixture
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)
    non_existent_cash_action_id = str(uuid.uuid4())

    response = client.delete(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}/cash_actions/{non_existent_cash_action_id}",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Cash action not found"
