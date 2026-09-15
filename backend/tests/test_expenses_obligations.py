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


def create_property_building_unit(
    client: TestClient,
    token: str,
    property_name: str,
    unit_number: str,
) -> tuple[int, int]:
    headers = auth_headers(token)

    property_response = client.post(
        "/api/properties/",
        headers=headers,
        json={
            "name": property_name,
            "address": f"{property_name} Street",
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
            "unit_number": unit_number,
            "status": "VACANT",
        },
    )

    unit_id = unit_response.json()["id"]

    return property_id, unit_id


def test_expense_unit_must_belong_to_same_property(
    client: TestClient,
):
    token = create_owner_and_token(client)

    property_a, _ = create_property_building_unit(
        client,
        token,
        "Cedar House",
        "101",
    )

    _, unit_b = create_property_building_unit(
        client,
        token,
        "Marina Court",
        "201",
    )

    response = client.post(
        f"/api/properties/{property_a}/expenses",
        headers=auth_headers(token),
        json={
            "unit_id": unit_b,
            "amount": 250.00,
            "category": "Plumbing",
            "expense_date": "2026-09-10",
            "description": "Repair",
        },
    )

    assert response.status_code == 400


def test_owner_can_create_rent_obligation_and_duplicate_is_rejected(
    client: TestClient,
):
    token = create_owner_and_token(client)
    headers = auth_headers(token)

    _, unit_id = create_property_building_unit(
        client,
        token,
        "Cedar House",
        "101",
    )

    tenant_response = client.post(
        "/api/tenants/",
        headers=headers,
        json={
            "email": "alice@test.com",
            "password": "TenantPass123!",
        },
    )

    tenant_id = tenant_response.json()["id"]

    lease_response = client.post(
        f"/api/units/{unit_id}/leases",
        headers=headers,
        json={
            "tenant_user_id": tenant_id,
            "start_date": "2026-01-01",
            "end_date": None,
            "rent_amount": 1500.00,
        },
    )

    assert lease_response.status_code == 201

    lease_id = lease_response.json()["id"]

    payload = {
        "amount": 1500.00,
        "due_date": "2026-10-01",
    }

    first = client.post(
        f"/api/leases/{lease_id}/obligations",
        headers=headers,
        json=payload,
    )

    second = client.post(
        f"/api/leases/{lease_id}/obligations",
        headers=headers,
        json=payload,
    )

    assert first.status_code == 201
    assert first.json()["status"] == "PENDING"

    assert second.status_code == 409


def test_ended_lease_cannot_receive_new_obligation(
    client: TestClient,
):
    token = create_owner_and_token(client)
    headers = auth_headers(token)

    _, unit_id = create_property_building_unit(
        client,
        token,
        "Cedar House",
        "101",
    )

    tenant_response = client.post(
        "/api/tenants/",
        headers=headers,
        json={
            "email": "alice@test.com",
            "password": "TenantPass123!",
        },
    )

    tenant_id = tenant_response.json()["id"]

    lease_response = client.post(
        f"/api/units/{unit_id}/leases",
        headers=headers,
        json={
            "tenant_user_id": tenant_id,
            "start_date": "2026-01-01",
            "end_date": None,
            "rent_amount": 1500.00,
        },
    )

    lease_id = lease_response.json()["id"]

    end_response = client.post(
        f"/api/leases/{lease_id}/end",
        headers=headers,
    )

    assert end_response.status_code == 200

    obligation_response = client.post(
        f"/api/leases/{lease_id}/obligations",
        headers=headers,
        json={
            "amount": 1500.00,
            "due_date": "2026-10-01",
        },
    )

    assert obligation_response.status_code == 409