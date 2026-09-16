from fastapi.testclient import TestClient


def auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
    }


def create_owner_and_token(
    client: TestClient,
    email: str = "owner@test.com",
    password: str = "StrongPass123!",
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


def create_unit(
    client: TestClient,
    token: str,
) -> int:
    headers = auth_headers(token)

    property_response = client.post(
        "/api/properties/",
        headers=headers,
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
        headers=headers,
        json={
            "name": "Main Building",
        },
    )

    building_id = building_response.json()["id"]

    unit_response = client.post(
        f"/api/buildings/{building_id}/units",
        headers=headers,
        json={
            "unit_number": "101",
            "status": "VACANT",
        },
    )

    return unit_response.json()["id"]


def create_maintenance(
    client: TestClient,
    token: str,
    unit_id: int,
) -> int:
    response = client.post(
        f"/api/units/{unit_id}/maintenance",
        headers=auth_headers(token),
        json={
            "category": "Plumbing",
            "description": (
                "Kitchen sink is leaking beneath the cabinet."
            ),
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "OPEN"

    return response.json()["id"]


def test_valid_maintenance_status_transitions(
    client: TestClient,
):
    token = create_owner_and_token(client)
    unit_id = create_unit(client, token)

    maintenance_id = create_maintenance(
        client,
        token,
        unit_id,
    )

    transitions = [
        "ASSIGNED",
        "IN_PROGRESS",
        "RESOLVED",
    ]

    for expected_status in transitions:
        response = client.patch(
            f"/api/maintenance/{maintenance_id}/status",
            headers=auth_headers(token),
            json={
                "status": expected_status,
            },
        )

        assert response.status_code == 200
        assert (
            response.json()["status"]
            == expected_status
        )

    final_response = client.get(
        f"/api/maintenance/{maintenance_id}",
        headers=auth_headers(token),
    )

    assert final_response.status_code == 200
    assert final_response.json()["status"] == "RESOLVED"
    assert final_response.json()["resolved_at"] is not None


def test_invalid_maintenance_transition_is_rejected(
    client: TestClient,
):
    token = create_owner_and_token(client)
    unit_id = create_unit(client, token)

    maintenance_id = create_maintenance(
        client,
        token,
        unit_id,
    )

    response = client.patch(
        f"/api/maintenance/{maintenance_id}/status",
        headers=auth_headers(token),
        json={
            "status": "RESOLVED",
        },
    )

    assert response.status_code == 409

    maintenance_response = client.get(
        f"/api/maintenance/{maintenance_id}",
        headers=auth_headers(token),
    )

    assert maintenance_response.json()["status"] == "OPEN"


def test_resolved_maintenance_cannot_be_reopened(
    client: TestClient,
):
    token = create_owner_and_token(client)
    unit_id = create_unit(client, token)

    maintenance_id = create_maintenance(
        client,
        token,
        unit_id,
    )

    for status_value in [
        "ASSIGNED",
        "IN_PROGRESS",
        "RESOLVED",
    ]:
        response = client.patch(
            f"/api/maintenance/{maintenance_id}/status",
            headers=auth_headers(token),
            json={
                "status": status_value,
            },
        )

        assert response.status_code == 200

    reopen_response = client.patch(
        f"/api/maintenance/{maintenance_id}/status",
        headers=auth_headers(token),
        json={
            "status": "OPEN",
        },
    )

    assert reopen_response.status_code == 409


def test_owner_cannot_access_another_owners_maintenance(
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

    unit_id = create_unit(
        client,
        owner_a,
    )

    maintenance_id = create_maintenance(
        client,
        owner_a,
        unit_id,
    )

    get_response = client.get(
        f"/api/maintenance/{maintenance_id}",
        headers=auth_headers(owner_b),
    )

    assert get_response.status_code == 404

    update_response = client.patch(
        f"/api/maintenance/{maintenance_id}/status",
        headers=auth_headers(owner_b),
        json={
            "status": "ASSIGNED",
        },
    )

    assert update_response.status_code == 404