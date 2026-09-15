from fastapi.testclient import TestClient


def create_owner_and_token(
    client: TestClient,
    email: str,
    password: str,
) -> str:
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
    }


def test_owner_cannot_access_another_owners_property(
    client: TestClient,
):
    owner_a_token = create_owner_and_token(
        client,
        "owner.a@test.com",
        "StrongPass123!",
    )

    owner_b_token = create_owner_and_token(
        client,
        "owner.b@test.com",
        "StrongPass456!",
    )

    create_response = client.post(
        "/api/properties/",
        headers=auth_headers(owner_a_token),
        json={
            "name": "Cedar House",
            "address": "12 Cedar Street",
            "city": "Sidon",
            "country": "Lebanon",
        },
    )

    assert create_response.status_code == 201

    property_id = create_response.json()["id"]

    owner_b_list = client.get(
        "/api/properties/",
        headers=auth_headers(owner_b_token),
    )

    assert owner_b_list.status_code == 200
    assert owner_b_list.json() == []

    cross_owner_response = client.get(
        f"/api/properties/{property_id}",
        headers=auth_headers(owner_b_token),
    )

    assert cross_owner_response.status_code == 404


def test_property_endpoints_require_authentication(
    client: TestClient,
):
    response = client.get("/api/properties/")

    assert response.status_code == 401