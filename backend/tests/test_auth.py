from fastapi.testclient import TestClient


def test_owner_can_register_and_login(client: TestClient):
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "owner@test.com",
            "password": "StrongPass123!",
        },
    )

    assert register_response.status_code == 201

    user = register_response.json()

    assert user["email"] == "owner@test.com"
    assert user["role"] == "OWNER"
    assert "password" not in user
    assert "password_hash" not in user

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "owner@test.com",
            "password": "StrongPass123!",
        },
    )

    assert login_response.status_code == 200
    assert login_response.json()["access_token"]


def test_duplicate_owner_email_is_rejected(client: TestClient):
    payload = {
        "email": "owner@test.com",
        "password": "StrongPass123!",
    }

    client.post("/api/auth/register", json=payload)

    response = client.post(
        "/api/auth/register",
        json=payload,
    )

    assert response.status_code == 409


def test_protected_endpoint_requires_authentication(
    client: TestClient,
):
    response = client.get("/api/auth/me")

    assert response.status_code == 401