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


def create_property_unit(
    client: TestClient,
    owner_token: str,
    property_name: str,
    unit_number: str,
) -> int:
    headers = auth_headers(owner_token)

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


def create_tenant_and_token(
    client: TestClient,
    owner_token: str,
    email: str,
    password: str,
) -> tuple[int, str]:
    tenant_response = client.post(
        "/api/tenants/",
        headers=auth_headers(owner_token),
        json={
            "email": email,
            "password": password,
        },
    )

    assert tenant_response.status_code == 201

    tenant_id = tenant_response.json()["id"]

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    return (
        tenant_id,
        login_response.json()["access_token"],
    )


def create_active_lease(
    client: TestClient,
    owner_token: str,
    unit_id: int,
    tenant_id: int,
) -> int:
    response = client.post(
        f"/api/units/{unit_id}/leases",
        headers=auth_headers(owner_token),
        json={
            "tenant_user_id": tenant_id,
            "start_date": "2026-01-01",
            "end_date": None,
            "rent_amount": 1500.00,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_tenant_can_submit_maintenance_for_active_unit(
    client: TestClient,
):
    owner_token = create_owner_and_token(client)

    unit_id = create_property_unit(
        client,
        owner_token,
        "Cedar House",
        "101",
    )

    tenant_id, tenant_token = create_tenant_and_token(
        client,
        owner_token,
        "alice@test.com",
        "TenantPass123!",
    )

    create_active_lease(
        client,
        owner_token,
        unit_id,
        tenant_id,
    )

    response = client.post(
        "/api/tenant/maintenance",
        headers=auth_headers(tenant_token),
        json={
            "category": "Plumbing",
            "description": (
                "Kitchen sink is leaking underneath the cabinet."
            ),
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "OPEN"
    assert data["unit_id"] == unit_id
    assert data["created_by_user_id"] == tenant_id


def test_tenant_without_active_lease_cannot_submit_maintenance(
    client: TestClient,
):
    owner_token = create_owner_and_token(client)

    _, tenant_token = create_tenant_and_token(
        client,
        owner_token,
        "alice@test.com",
        "TenantPass123!",
    )

    response = client.post(
        "/api/tenant/maintenance",
        headers=auth_headers(tenant_token),
        json={
            "category": "Plumbing",
            "description": (
                "Kitchen sink is leaking underneath the cabinet."
            ),
        },
    )

    assert response.status_code == 404


def test_tenant_cannot_access_other_tenants_maintenance(
    client: TestClient,
):
    owner_token = create_owner_and_token(client)

    unit_a = create_property_unit(
        client,
        owner_token,
        "Cedar House",
        "101",
    )

    unit_b = create_property_unit(
        client,
        owner_token,
        "Harbor View",
        "A1",
    )

    tenant_a_id, tenant_a_token = create_tenant_and_token(
        client,
        owner_token,
        "alice@test.com",
        "TenantPass123!",
    )

    tenant_b_id, tenant_b_token = create_tenant_and_token(
        client,
        owner_token,
        "bob@test.com",
        "TenantPass456!",
    )

    create_active_lease(
        client,
        owner_token,
        unit_a,
        tenant_a_id,
    )

    create_active_lease(
        client,
        owner_token,
        unit_b,
        tenant_b_id,
    )

    create_response = client.post(
        "/api/tenant/maintenance",
        headers=auth_headers(tenant_a_token),
        json={
            "category": "Electrical",
            "description": (
                "The bedroom wall outlet is not working."
            ),
        },
    )

    assert create_response.status_code == 201

    maintenance_id = create_response.json()["id"]

    forbidden_response = client.get(
        f"/api/tenant/maintenance/{maintenance_id}",
        headers=auth_headers(tenant_b_token),
    )

    assert forbidden_response.status_code == 404


def test_tenant_cannot_change_maintenance_status(
    client: TestClient,
):
    owner_token = create_owner_and_token(client)

    unit_id = create_property_unit(
        client,
        owner_token,
        "Cedar House",
        "101",
    )

    tenant_id, tenant_token = create_tenant_and_token(
        client,
        owner_token,
        "alice@test.com",
        "TenantPass123!",
    )

    create_active_lease(
        client,
        owner_token,
        unit_id,
        tenant_id,
    )

    create_response = client.post(
        "/api/tenant/maintenance",
        headers=auth_headers(tenant_token),
        json={
            "category": "Plumbing",
            "description": (
                "The bathroom faucet is leaking continuously."
            ),
        },
    )

    maintenance_id = create_response.json()["id"]

    response = client.patch(
        f"/api/maintenance/{maintenance_id}/status",
        headers=auth_headers(tenant_token),
        json={
            "status": "ASSIGNED",
        },
    )

    assert response.status_code == 403


def test_owner_can_see_and_manage_tenant_created_maintenance(
    client: TestClient,
):
    owner_token = create_owner_and_token(client)

    unit_id = create_property_unit(
        client,
        owner_token,
        "Cedar House",
        "101",
    )

    tenant_id, tenant_token = create_tenant_and_token(
        client,
        owner_token,
        "alice@test.com",
        "TenantPass123!",
    )

    create_active_lease(
        client,
        owner_token,
        unit_id,
        tenant_id,
    )

    create_response = client.post(
        "/api/tenant/maintenance",
        headers=auth_headers(tenant_token),
        json={
            "category": "Plumbing",
            "description": (
                "The kitchen sink drain is leaking."
            ),
        },
    )

    assert create_response.status_code == 201

    maintenance_id = create_response.json()["id"]

    owner_list_response = client.get(
        f"/api/units/{unit_id}/maintenance",
        headers=auth_headers(owner_token),
    )

    assert owner_list_response.status_code == 200

    maintenance_ids = {
        item["id"]
        for item in owner_list_response.json()
    }

    assert maintenance_id in maintenance_ids

    status_response = client.patch(
        f"/api/maintenance/{maintenance_id}/status",
        headers=auth_headers(owner_token),
        json={
            "status": "ASSIGNED",
        },
    )

    assert status_response.status_code == 200
    assert status_response.json()["status"] == "ASSIGNED"

    tenant_view_response = client.get(
        f"/api/tenant/maintenance/{maintenance_id}",
        headers=auth_headers(tenant_token),
    )

    assert tenant_view_response.status_code == 200
    assert (
        tenant_view_response.json()["status"]
        == "ASSIGNED"
    )