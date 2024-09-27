import uuid
from datetime import timedelta

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import create_access_token, hash_password


def authenticate_user(client: TestClient, user):
    """Helper function to authenticate and return headers."""
    access_token = create_access_token(
        user.id, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"Authorization": f"Bearer {access_token}"}


def test_register_user_success(client: TestClient):
    register_data = {
        "email": "newuser@example.com",
        "password": "newpassword",
    }

    response = client.post(f"{settings.API_V1_STR}/users/signup", json=register_data)

    assert response.status_code == 201
    json_response = response.json()
    assert json_response["email"] == register_data["email"]


def test_register_user_already_exists(client: TestClient, create_user_fixture):
    existing_user = create_user_fixture()

    register_data = {
        "email": existing_user.email,
        "password": "newpassword",
    }

    response = client.post(f"{settings.API_V1_STR}/users/signup", json=register_data)

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "The user with this email already exists in the system"
    )


def test_read_user_me_success(client: TestClient, create_user_fixture):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["email"] == user.email
    assert json_response["id"] == str(user.id)


def test_update_user_me_success(client: TestClient, create_user_fixture):
    user = create_user_fixture()
    headers = authenticate_user(client, user)

    update_data = {
        "email": "updateduser@example.com",
    }

    response = client.patch(
        f"{settings.API_V1_STR}/users/me", json=update_data, headers=headers
    )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["email"] == update_data["email"]


def test_update_user_me_email_conflict(client: TestClient, create_user_fixture):
    user1 = create_user_fixture(email="user1@example.com")
    user2 = create_user_fixture(email="user2@example.com")
    headers = authenticate_user(client, user1)

    update_data = {
        "email": user2.email,  # Trying to update with another user's email
    }

    response = client.patch(
        f"{settings.API_V1_STR}/users/me", json=update_data, headers=headers
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists"


def test_update_password_me_success(client: TestClient, create_user_fixture):
    user = create_user_fixture(password=hash_password("oldpassword"))
    headers = authenticate_user(client, user)

    password_update_data = {
        "current_password": "oldpassword",
        "new_password": "newpassword",
    }

    response = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        json=password_update_data,
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"


def test_update_password_me_incorrect_current_password(
    client: TestClient, create_user_fixture
):
    user = create_user_fixture(password=hash_password("oldpassword"))
    headers = authenticate_user(client, user)

    password_update_data = {
        "current_password": "wrongpassword",  # Incorrect current password
        "new_password": "newpassword",
    }

    response = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        json=password_update_data,
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect password"


def test_delete_user_me_success(client: TestClient, create_user_fixture):
    user = create_user_fixture(is_superuser=False)
    headers = authenticate_user(client, user)

    response = client.delete(f"{settings.API_V1_STR}/users/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"


def test_delete_user_me_superuser_forbidden(client: TestClient, create_user_fixture):
    user = create_user_fixture(is_superuser=True)
    headers = authenticate_user(client, user)

    response = client.delete(f"{settings.API_V1_STR}/users/me", headers=headers)

    assert response.status_code == 403
    assert (
        response.json()["detail"] == "Super users are not allowed to delete themselves"
    )


# Superuser-related tests


def test_read_user_by_id_success(client: TestClient, create_user_fixture):
    superuser = create_user_fixture(is_superuser=True)
    user = create_user_fixture()
    headers = authenticate_user(client, superuser)

    response = client.get(f"{settings.API_V1_STR}/admin/users/{user.id}", headers=headers)

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["email"] == user.email
    assert json_response["id"] == str(user.id)


def test_read_user_by_id_not_found(client: TestClient, create_user_fixture):
    superuser = create_user_fixture(is_superuser=True)
    headers = authenticate_user(client, superuser)

    non_existent_id = str(uuid.uuid4())
    response = client.get(
        f"{settings.API_V1_STR}/admin/users/{non_existent_id}", headers=headers
    )

    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == "The user with this id does not exist in the system"
    )


def test_superuser_create_user_success(client: TestClient, create_user_fixture):
    superuser = create_user_fixture(is_superuser=True)
    headers = authenticate_user(client, superuser)

    new_user_data = {
        "email": "newadminuser@example.com",
        "password": "newpassword",
    }

    response = client.post(
        f"{settings.API_V1_STR}/admin/users/", json=new_user_data, headers=headers
    )

    assert response.status_code == 201
    json_response = response.json()
    assert json_response["email"] == new_user_data["email"]


def test_superuser_update_user_success(client: TestClient, create_user_fixture):
    superuser = create_user_fixture(is_superuser=True)
    user = create_user_fixture()
    headers = authenticate_user(client, superuser)

    update_data = {
        "email": "updateduser@example.com",
    }

    response = client.patch(
        f"{settings.API_V1_STR}/admin/users/{user.id}", json=update_data, headers=headers
    )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["email"] == update_data["email"]


def test_superuser_delete_user_success(client: TestClient, create_user_fixture):
    superuser = create_user_fixture(is_superuser=True)
    user = create_user_fixture()
    headers = authenticate_user(client, superuser)

    response = client.delete(f"{settings.API_V1_STR}/admin/users/{user.id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"


def test_superuser_delete_user_not_found(client: TestClient, create_user_fixture):
    superuser = create_user_fixture(is_superuser=True)
    headers = authenticate_user(client, superuser)

    non_existent_id = str(uuid.uuid4())
    response = client.delete(
        f"{settings.API_V1_STR}/admin/users/{non_existent_id}", headers=headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
