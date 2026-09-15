from fastapi.testclient import TestClient


def create_owner_and_token(
    client: TestClient,
    email: str,
    password: str,
) -> str:
    client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    return login_response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
    }


def test_owner_cannot_access_another_owners_building_or_unit(
    client: TestClient,
):
    owner_a = create_owner_and_token(
        client,
        "owner.a@test.com",
        "StrongPass123!",
    )

    owner_b = create_owner_and_token(
        client,
        "owner.b@test.com",
        "StrongPass456!",
    )

    property_response = client.post(
        "/api/properties/",
        headers=auth_headers(owner_a),
        json={
            "name": "Cedar House",
            "address": "12 Cedar Street",
            "city": "Sidon",
            "country": "Lebanon",
        },
    )

    property_id = property_response.json()["id"]

    building_response = client.post(
        f"/api/properties/{property_id}/buildings",
        headers=auth_headers(owner_a),
        json={
            "name": "Main Building",
        },
    )

    assert building_response.status_code == 201

    building_id = building_response.json()["id"]

    unit_response = client.post(
        f"/api/buildings/{building_id}/units",
        headers=auth_headers(owner_a),
        json={
            "unit_number": "101",
            "status": "VACANT",
        },
    )

    assert unit_response.status_code == 201

    unit_id = unit_response.json()["id"]

    forbidden_building = client.get(
        f"/api/buildings/{building_id}",
        headers=auth_headers(owner_b),
    )

    forbidden_unit = client.get(
        f"/api/units/{unit_id}",
        headers=auth_headers(owner_b),
    )

    assert forbidden_building.status_code == 404
    assert forbidden_unit.status_code == 404


def test_duplicate_unit_number_in_same_building_is_rejected(
    client: TestClient,
):
    token = create_owner_and_token(
        client,
        "owner@test.com",
        "StrongPass123!",
    )

    property_response = client.post(
        "/api/properties/",
        headers=auth_headers(token),
        json={
            "name": "Cedar House",
            "address": "12 Cedar Street",
            "city": "Sidon",
            "country": "Lebanon",
        },
    )

    property_id = property_response.json()["id"]

    building_response = client.post(
        f"/api/properties/{property_id}/buildings",
        headers=auth_headers(token),
        json={
            "name": "Main Building",
        },
    )

    building_id = building_response.json()["id"]

    payload = {
        "unit_number": "101",
        "status": "VACANT",
    }

    first = client.post(
        f"/api/buildings/{building_id}/units",
        headers=auth_headers(token),
        json=payload,
    )

    second = client.post(
        f"/api/buildings/{building_id}/units",
        headers=auth_headers(token),
        json=payload,
    )

    assert first.status_code == 201
    assert second.status_code == 409