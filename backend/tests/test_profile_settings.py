from fastapi.testclient import TestClient


def register_owner(
    client: TestClient,
):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "profile@test.com",
            "password": "StrongPass123!",
        },
    )

    assert response.status_code == 201


def login(
    client: TestClient,
    password: str = "StrongPass123!",
):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "profile@test.com",
            "password": password,
        },
    )

    return response


def headers(
    token: str,
):
    return {
        "Authorization":
            f"Bearer {token}",
    }


def test_user_can_update_profile(
    client: TestClient,
):
    register_owner(client)

    login_response = login(
        client
    )

    token = (
        login_response.json()[
            "access_token"
        ]
    )

    response = client.patch(
        "/api/auth/me/profile",
        headers=headers(token),
        json={
            "first_name":
                "Sirine",
            "last_name":
                "Zamzam",
            "phone_number":
                "+961 70 123 456",
            "email":
                "updated@test.com",
        },
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        data["first_name"]
        == "Sirine"
    )

    assert (
        data["last_name"]
        == "Zamzam"
    )

    assert (
        data["phone_number"]
        == "+961 70 123 456"
    )

    assert (
        data["email"]
        == "updated@test.com"
    )


def test_user_can_change_password(
    client: TestClient,
):
    register_owner(client)

    login_response = login(
        client
    )

    token = (
        login_response.json()[
            "access_token"
        ]
    )

    response = client.patch(
        "/api/auth/me/password",
        headers=headers(token),
        json={
            "current_password":
                "StrongPass123!",
            "new_password":
                "NewStrongPass456!",
        },
    )

    assert (
        response.status_code
        == 204
    )

    old_login = client.post(
        "/api/auth/login",
        json={
            "email":
                "profile@test.com",
            "password":
                "StrongPass123!",
        },
    )

    assert (
        old_login.status_code
        == 401
    )

    new_login = client.post(
        "/api/auth/login",
        json={
            "email":
                "profile@test.com",
            "password":
                "NewStrongPass456!",
        },
    )

    assert (
        new_login.status_code
        == 200
    )


def test_wrong_current_password_is_rejected(
    client: TestClient,
):
    register_owner(client)

    token = (
        login(client).json()[
            "access_token"
        ]
    )

    response = client.patch(
        "/api/auth/me/password",
        headers=headers(token),
        json={
            "current_password":
                "WrongPass123!",
            "new_password":
                "NewStrongPass456!",
        },
    )

    assert (
        response.status_code
        == 400
    )