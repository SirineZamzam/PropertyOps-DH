from datetime import (
    datetime,
    timezone,
)

from fastapi.testclient import (
    TestClient,
)

from app.api.routes import (
    ai_analysis,
)

from app.core.security import (
    create_access_token,
    hash_password,
)

from app.models.ai_analysis_job import (
    AIAnalysisJob,
    AIAnalysisScope,
    AIJobStatus,
)

from app.models.building import (
    Building,
)

from app.models.maintenance import (
    Maintenance,
    MaintenanceStatus,
)

from app.models.property import (
    Property,
)

from app.models.unit import (
    Unit,
    UnitStatus,
)

from app.models.user import (
    User,
    UserRole,
)


def auth_headers(
    token: str,
) -> dict[str, str]:
    return {
        "Authorization":
            f"Bearer {token}",
    }


def create_user(
    db,
    email: str,
    role: UserRole,
) -> tuple[User, str]:
    user = User(
        email=email,
        password_hash=(
            hash_password(
                "StrongPass123!"
            )
        ),
        role=role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        user.id
    )

    return user, token


def create_property_with_history(
    db,
    owner: User,
) -> Property:
    property_record = Property(
        owner_id=owner.id,
        name="AI Property",
        address="20 AI Street",
        city="Sidon",
        country="Lebanon",
    )

    db.add(property_record)
    db.flush()

    building = Building(
        property_id=(
            property_record.id
        ),
        name="Main Building",
    )

    db.add(building)
    db.flush()

    unit = Unit(
        building_id=building.id,
        unit_number="101",
        status=UnitStatus.VACANT,
    )

    db.add(unit)
    db.flush()

    maintenance = Maintenance(
        unit_id=unit.id,
        created_by_user_id=(
            owner.id
        ),
        category="Plumbing",
        description=(
            "Kitchen sink leaking."
        ),
        status=(
            MaintenanceStatus.OPEN
        ),
    )

    db.add(maintenance)
    db.commit()
    db.refresh(property_record)

    return property_record


def test_ai_analysis_rejects_cross_owner(
    client: TestClient,
    db,
    monkeypatch,
):
    owner_a, _ = create_user(
        db,
        "owner.a.ai@test.com",
        UserRole.OWNER,
    )

    _, owner_b_token = (
        create_user(
            db,
            "owner.b.ai@test.com",
            UserRole.OWNER,
        )
    )

    property_record = (
        create_property_with_history(
            db,
            owner_a,
        )
    )

    monkeypatch.setattr(
        ai_analysis,
        "process_ai_job",
        lambda job_id: None,
    )

    response = client.post(
        (
            "/api/owner/ai/properties/"
            f"{property_record.id}/analysis"
        ),
        headers=auth_headers(
            owner_b_token
        ),
    )

    assert response.status_code == 404


def test_tenant_cannot_request_ai_analysis(
    client: TestClient,
    db,
):
    _, tenant_token = (
        create_user(
            db,
            "tenant.ai@test.com",
            UserRole.TENANT,
        )
    )

    response = client.post(
        (
            "/api/owner/ai/properties/"
            "999/analysis"
        ),
        headers=auth_headers(
            tenant_token
        ),
    )

    assert response.status_code == 403


def test_ai_analysis_requires_history(
    client: TestClient,
    db,
    monkeypatch,
):
    owner, token = create_user(
        db,
        "empty.ai@test.com",
        UserRole.OWNER,
    )

    property_record = Property(
        owner_id=owner.id,
        name="Empty Property",
        address="30 Empty Street",
        city="Sidon",
        country="Lebanon",
    )

    db.add(property_record)
    db.commit()
    db.refresh(property_record)

    monkeypatch.setattr(
        ai_analysis,
        "process_ai_job",
        lambda job_id: None,
    )

    response = client.post(
        (
            "/api/owner/ai/properties/"
            f"{property_record.id}/analysis"
        ),
        headers=auth_headers(
            token
        ),
    )

    assert response.status_code == 409


def test_duplicate_running_ai_job_is_rejected(
    client: TestClient,
    db,
    monkeypatch,
):
    owner, token = create_user(
        db,
        "duplicate.ai@test.com",
        UserRole.OWNER,
    )

    property_record = (
        create_property_with_history(
            db,
            owner,
        )
    )

    job = AIAnalysisJob(
        owner_user_id=owner.id,
        scope_type=(
            AIAnalysisScope.PROPERTY
        ),
        property_id=(
            property_record.id
        ),
        status=AIJobStatus.PENDING,
    )

    db.add(job)
    db.commit()

    monkeypatch.setattr(
        ai_analysis,
        "process_ai_job",
        lambda job_id: None,
    )

    response = client.post(
        (
            "/api/owner/ai/properties/"
            f"{property_record.id}/analysis"
        ),
        headers=auth_headers(
            token
        ),
    )

    assert response.status_code == 409


def test_ai_rate_limit_is_enforced(
    client: TestClient,
    db,
    monkeypatch,
):
    owner, token = create_user(
        db,
        "limit.ai@test.com",
        UserRole.OWNER,
    )

    property_record = (
        create_property_with_history(
            db,
            owner,
        )
    )

    for _ in range(5):
        db.add(
            AIAnalysisJob(
                owner_user_id=owner.id,

                scope_type=(
                    AIAnalysisScope.PROPERTY
                ),

                property_id=(
                    property_record.id
                ),

                status=(
                    AIJobStatus.COMPLETED
                ),

                created_at=(
                    datetime.now(
                        timezone.utc
                    )
                ),
            )
        )

    db.commit()

    monkeypatch.setattr(
        ai_analysis,
        "process_ai_job",
        lambda job_id: None,
    )

    response = client.post(
        (
            "/api/owner/ai/properties/"
            f"{property_record.id}/analysis"
        ),
        headers=auth_headers(
            token
        ),
    )

    assert response.status_code == 429