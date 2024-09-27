from datetime import timedelta

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import create_access_token, hash_password


def test_login_access_token_success(client: TestClient, create_user_fixture):
    create_user_fixture(
        email="testuser@example.com", password=hash_password("testpassword")
    )
    login_data = {
        "username": "testuser@example.com",
        "password": "testpassword",
    }
    response = client.post(f"{settings.API_V1_STR}/login", data=login_data)

    assert response.status_code == 200
    json_response = response.json()
    assert "access_token" in json_response
    assert json_response["access_token"] is not None


def test_login_access_token_failure(client: TestClient):
    login_data = {
        "username": "wronguser@example.com",
        "password": "wrongpassword",
    }
    response = client.post(f"{settings.API_V1_STR}/login", data=login_data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"


def test_reset_password_success(client: TestClient, create_user_fixture, mocker):
    user = create_user_fixture(email="testuser@example.com", password="oldpassword")
    mocker.patch(
        "app.core.security.verify_password_reset_token", return_value=user.email
    )

    reset_data = {
        "token": "valid_token",
        "new_password": "newpassword",
    }
    response = client.post(f"{settings.API_V1_STR}/reset-password/", json=reset_data)

    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"


def test_reset_password_invalid_token(client: TestClient):
    reset_data = {
        "token": "invalid_token",
        "new_password": "newpassword",
    }
    response = client.post(f"{settings.API_V1_STR}/reset-password/", json=reset_data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid token"


def test_recover_password_html_content_success(
    client: TestClient, create_user_fixture, mocker
):
    superuser = create_user_fixture(
        email="testsuperuser@example.com", password="password", is_superuser=True
    )
    mocker.patch(
        "app.core.security.generate_password_reset_token", return_value="reset_token"
    )

    access_token = create_access_token(
        superuser.id, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post(
        f"{settings.API_V1_STR}/admin/recover-password/{superuser.email}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "reset_token"


def test_recover_password_html_content_user_not_found(
    client: TestClient, create_user_fixture, mocker
):
    superuser = create_user_fixture(
        email="admin@example.com", password="adminpassword", is_superuser=True
    )
    access_token = create_access_token(
        superuser.id, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    headers = {"Authorization": f"Bearer {access_token}"}

    mocker.patch(
        "app.core.security.generate_password_reset_token", return_value="reset_token"
    )
    response = client.post(
        f"{settings.API_V1_STR}/admin/recover-password/nonexistentuser@example.com",
        headers=headers,
    )

    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == "The user with this username does not exist in the system."
    )
