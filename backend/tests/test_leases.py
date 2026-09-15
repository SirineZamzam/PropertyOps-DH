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
    unit_number: str = "101",
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

    assert property_response.status_code == 201
    property_id = property_response.json()["id"]

    building_response = client.post(
        f"/api/properties/{property_id}/buildings",
        headers=headers,
        json={
            "name": "Main Building",
        },
    )

    assert building_response.status_code == 201
    building_id = building_response.json()["id"]

    unit_response = client.post(
        f"/api/buildings/{building_id}/units",
        headers=headers,
        json={
            "unit_number": unit_number,
            "status": "VACANT",
        },
    )

    assert unit_response.status_code == 201

    return unit_response.json()["id"]


def create_tenant(
    client: TestClient,
    token: str,
    email: str,
    password: str,
) -> int:
    response = client.post(
        "/api/tenants/",
        headers=auth_headers(token),
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201

    tenant = response.json()

    assert tenant["role"] == "TENANT"
    assert tenant["email"] == email

    return tenant["id"]


def test_owner_can_provision_tenant(
    client: TestClient,
):
    token = create_owner_and_token(client)

    response = client.post(
        "/api/tenants/",
        headers=auth_headers(token),
        json={
            "email": "alice@test.com",
            "password": "TenantPass123!",
        },
    )

    assert response.status_code == 201

    tenant = response.json()

    assert tenant["email"] == "alice@test.com"
    assert tenant["role"] == "TENANT"
    assert tenant["is_active"] is True
    assert "password" not in tenant
    assert "password_hash" not in tenant


def test_lease_lifecycle_and_historical_leases(
    client: TestClient,
):
    token = create_owner_and_token(client)

    unit_id = create_unit(
        client,
        token,
    )

    alice_id = create_tenant(
        client,
        token,
        "alice@test.com",
        "TenantPass123!",
    )

    # 1. Create Alice's active lease.
    alice_lease_response = client.post(
        f"/api/units/{unit_id}/leases",
        headers=auth_headers(token),
        json={
            "tenant_user_id": alice_id,
            "start_date": "2026-01-01",
            "end_date": None,
            "rent_amount": 1500.00,
        },
    )

    assert alice_lease_response.status_code == 201

    alice_lease = alice_lease_response.json()

    assert alice_lease["status"] == "ACTIVE"
    assert alice_lease["unit_id"] == unit_id
    assert alice_lease["tenant_user_id"] == alice_id

    alice_lease_id = alice_lease["id"]

    # 2. Active lease makes the Unit OCCUPIED.
    unit_response = client.get(
        f"/api/units/{unit_id}",
        headers=auth_headers(token),
    )

    assert unit_response.status_code == 200
    assert unit_response.json()["status"] == "OCCUPIED"

    # Create Bob.
    bob_id = create_tenant(
        client,
        token,
        "bob@test.com",
        "TenantPass456!",
    )

    # 3. Second ACTIVE lease for the same Unit must fail.
    duplicate_active_response = client.post(
        f"/api/units/{unit_id}/leases",
        headers=auth_headers(token),
        json={
            "tenant_user_id": bob_id,
            "start_date": "2026-06-01",
            "end_date": None,
            "rent_amount": 1600.00,
        },
    )

    assert duplicate_active_response.status_code == 409

    # 4. End Alice's lease.
    end_response = client.post(
        f"/api/leases/{alice_lease_id}/end",
        headers=auth_headers(token),
    )

    assert end_response.status_code == 200
    assert end_response.json()["status"] == "ENDED"
    assert end_response.json()["end_date"] is not None

    # Unit should now become VACANT.
    unit_after_end = client.get(
        f"/api/units/{unit_id}",
        headers=auth_headers(token),
    )

    assert unit_after_end.status_code == 200
    assert unit_after_end.json()["status"] == "VACANT"

    # 5. Bob can now receive a new active lease.
    bob_lease_response = client.post(
        f"/api/units/{unit_id}/leases",
        headers=auth_headers(token),
        json={
            "tenant_user_id": bob_id,
            "start_date": "2026-07-01",
            "end_date": None,
            "rent_amount": 1600.00,
        },
    )

    assert bob_lease_response.status_code == 201
    assert bob_lease_response.json()["status"] == "ACTIVE"

    # Unit becomes OCCUPIED again.
    unit_after_bob = client.get(
        f"/api/units/{unit_id}",
        headers=auth_headers(token),
    )

    assert unit_after_bob.status_code == 200
    assert unit_after_bob.json()["status"] == "OCCUPIED"

    # 6. Both historical leases remain.
    history_response = client.get(
        f"/api/units/{unit_id}/leases",
        headers=auth_headers(token),
    )

    assert history_response.status_code == 200

    leases = history_response.json()

    assert len(leases) == 2

    statuses = {lease["status"] for lease in leases}

    assert statuses == {
        "ACTIVE",
        "ENDED",
    }

    tenant_ids = {
        lease["tenant_user_id"]
        for lease in leases
    }

    assert tenant_ids == {
        alice_id,
        bob_id,
    }