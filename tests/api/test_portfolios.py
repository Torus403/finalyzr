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


def test_create_portfolio_success(client: TestClient, create_user_fixture):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio_data = {
        "name": "My Test Portfolio",
        "description": "A portfolio created during tests.",
    }

    response = client.post(
        f"{settings.API_V1_STR}/portfolios/", json=portfolio_data, headers=headers
    )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["name"] == portfolio_data["name"]
    assert json_response["description"] == portfolio_data["description"]
    assert json_response["owner_id"] == str(user.id)


def test_create_portfolio_unauthorized(client: TestClient):
    portfolio_data = {
        "name": "Unauthorized Portfolio",
        "description": "Attempted creation without authentication.",
    }

    response = client.post(f"{settings.API_V1_STR}/portfolios/", json=portfolio_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_read_portfolios_success(
    client: TestClient, create_user_fixture, create_portfolio_fixture
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    create_portfolio_fixture(owner_id=user.id)
    create_portfolio_fixture(owner_id=user.id)

    response = client.get(f"{settings.API_V1_STR}/portfolios/", headers=headers)

    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response["portfolios"]) == 2


def test_read_portfolio_by_id_success(
    client: TestClient, create_user_fixture, create_portfolio_fixture
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)

    response = client.get(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}", headers=headers
    )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["id"] == str(portfolio.id)
    assert json_response["name"] == portfolio.name
    assert json_response["description"] == portfolio.description


def test_read_portfolio_by_id_not_found(client: TestClient, create_user_fixture):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    non_existent_id = str(uuid.uuid4())
    response = client.get(
        f"{settings.API_V1_STR}/portfolios/{non_existent_id}", headers=headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Portfolio not found"


def test_update_portfolio_success(
    client: TestClient, create_user_fixture, create_portfolio_fixture
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)

    updated_data = {
        "name": "Updated Portfolio Name",
        "description": "Updated description.",
    }

    response = client.put(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}",
        json=updated_data,
        headers=headers,
    )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["name"] == updated_data["name"]
    assert json_response["description"] == updated_data["description"]


def test_update_portfolio_unauthorized(
    client: TestClient, create_user_fixture, create_portfolio_fixture
):
    user = create_user_fixture()
    another_user = create_user_fixture()

    portfolio = create_portfolio_fixture(owner_id=another_user.id)
    headers = authenticate_user(client, user)

    updated_data = {
        "name": "Unauthorized Update",
        "description": "User should not be able to update this.",
    }

    response = client.put(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}",
        json=updated_data,
        headers=headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to update this portfolio"


def test_delete_portfolio_success(
    client: TestClient, create_user_fixture, create_portfolio_fixture
):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    portfolio = create_portfolio_fixture(owner_id=user.id)

    response = client.delete(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}", headers=headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Portfolio deleted successfully"


def test_delete_portfolio_unauthorized(
    client: TestClient, create_user_fixture, create_portfolio_fixture
):
    user = create_user_fixture()
    another_user = create_user_fixture()

    portfolio = create_portfolio_fixture(owner_id=another_user.id)
    headers = authenticate_user(client, user)

    response = client.delete(
        f"{settings.API_V1_STR}/portfolios/{portfolio.id}", headers=headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to delete this portfolio"


def test_delete_portfolio_not_found(client: TestClient, create_user_fixture):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    non_existent_id = str(uuid.uuid4())
    response = client.delete(
        f"{settings.API_V1_STR}/portfolios/{non_existent_id}", headers=headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Portfolio not found"
