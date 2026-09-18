from datetime import date

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.building import Building
from app.models.expense import Expense
from app.models.lease import Lease, LeaseStatus
from app.models.maintenance import (
    Maintenance,
    MaintenanceStatus,
)
from app.models.property import Property
from app.models.rent_obligation import (
    RentObligation,
    RentObligationStatus,
)
from app.models.unit import Unit, UnitStatus
from app.models.user import User, UserRole


def clear_existing_data(db: Session) -> None:
    """
    Clear development/demo data in child-to-parent order.

    This intentionally resets application data in the local development
    database. It must never be run blindly against production.
    """

    db.execute(delete(RentObligation))
    db.execute(delete(Expense))
    db.execute(delete(Maintenance))
    db.execute(delete(Lease))
    db.execute(delete(Unit))
    db.execute(delete(Building))
    db.execute(delete(Property))
    db.execute(delete(User))

    db.commit()


def seed_users(
    db: Session,
) -> dict[str, User]:
    users = {
        "owner_a": User(
            first_name="Nadine",
            last_name="Haddad",
            phone_number="+961 70 111 201",
            email="owner.a@propertyops.dev",
            password_hash=hash_password(
                "StrongPass123!"
            ),
            role=UserRole.OWNER,
        ),

        "owner_b": User(
            first_name="Karim",
            last_name="Salem",
            phone_number="+961 71 222 302",
            email="owner.b@propertyops.dev",
            password_hash=hash_password(
                "StrongPass456!"
            ),
            role=UserRole.OWNER,
        ),

        "alice": User(
            first_name="Alice",
            last_name="Mansour",
            phone_number="+961 76 301 410",
            email="alice@propertyops.dev",
            password_hash=hash_password(
                "TenantPass123!"
            ),
            role=UserRole.TENANT,
        ),

        "bob": User(
            first_name="Bob",
            last_name="Khoury",
            phone_number="+961 81 402 511",
            email="bob@propertyops.dev",
            password_hash=hash_password(
                "TenantPass456!"
            ),
            role=UserRole.TENANT,
        ),

        "carla": User(
            first_name="Carla",
            last_name="Nassar",
            phone_number="+961 70 503 612",
            email="carla@propertyops.dev",
            password_hash=hash_password(
                "TenantPass789!"
            ),
            role=UserRole.TENANT,
        ),

        "david": User(
            first_name="David",
            last_name="Farah",
            phone_number="+961 03 604 713",
            email="david@propertyops.dev",
            password_hash=hash_password(
                "TenantPass321!"
            ),
            role=UserRole.TENANT,
        ),
    }

    db.add_all(
        users.values()
    )

    db.flush()

    return users

def seed_properties_and_units(
    db: Session,
    users: dict[str, User],
) -> dict[str, object]:
    cedar = Property(
        owner_id=users["owner_a"].id,
        name="Cedar House",
        address="12 Cedar Street",
        city="Sidon",
        country="Lebanon",
    )

    harbor = Property(
        owner_id=users["owner_a"].id,
        name="Harbor View",
        address="8 Marina Road",
        city="Sidon",
        country="Lebanon",
    )

    pine = Property(
        owner_id=users["owner_b"].id,
        name="Pine Court",
        address="42 Pine Avenue",
        city="Beirut",
        country="Lebanon",
    )

    garden = Property(
        owner_id=users["owner_b"].id,
        name="Garden Residences",
        address="18 Garden Lane",
        city="Beirut",
        country="Lebanon",
    )

    db.add_all([
        cedar,
        harbor,
        pine,
        garden,
    ])

    db.flush()

    cedar_main = Building(
        property_id=cedar.id,
        name="Main Building",
    )

    cedar_annex = Building(
        property_id=cedar.id,
        name="Annex",
    )

    harbor_main = Building(
        property_id=harbor.id,
        name="Harbor Building",
    )

    pine_main = Building(
        property_id=pine.id,
        name="Pine Building",
    )

    garden_main = Building(
        property_id=garden.id,
        name="Garden Building",
    )

    db.add_all([
        cedar_main,
        cedar_annex,
        harbor_main,
        pine_main,
        garden_main,
    ])

    db.flush()

    units = {
        "cedar_101": Unit(
            building_id=cedar_main.id,
            unit_number="101",
            status=UnitStatus.OCCUPIED,
        ),
        "cedar_102": Unit(
            building_id=cedar_main.id,
            unit_number="102",
            status=UnitStatus.VACANT,
        ),
        "cedar_103": Unit(
            building_id=cedar_main.id,
            unit_number="103",
            status=UnitStatus.UNAVAILABLE,
        ),
        "cedar_201": Unit(
            building_id=cedar_annex.id,
            unit_number="201",
            status=UnitStatus.VACANT,
        ),
        "cedar_202": Unit(
            building_id=cedar_annex.id,
            unit_number="202",
            status=UnitStatus.VACANT,
        ),
        "harbor_a1": Unit(
            building_id=harbor_main.id,
            unit_number="A1",
            status=UnitStatus.OCCUPIED,
        ),
        "harbor_a2": Unit(
            building_id=harbor_main.id,
            unit_number="A2",
            status=UnitStatus.VACANT,
        ),
        "harbor_a3": Unit(
            building_id=harbor_main.id,
            unit_number="A3",
            status=UnitStatus.VACANT,
        ),
        "pine_1a": Unit(
            building_id=pine_main.id,
            unit_number="1A",
            status=UnitStatus.OCCUPIED,
        ),
        "pine_1b": Unit(
            building_id=pine_main.id,
            unit_number="1B",
            status=UnitStatus.VACANT,
        ),
        "garden_g1": Unit(
            building_id=garden_main.id,
            unit_number="G1",
            status=UnitStatus.OCCUPIED,
        ),
        "garden_g2": Unit(
            building_id=garden_main.id,
            unit_number="G2",
            status=UnitStatus.VACANT,
        ),
    }

    db.add_all(units.values())
    db.flush()

    return {
        "cedar": cedar,
        "harbor": harbor,
        "pine": pine,
        "garden": garden,
        **units,
    }


def seed_leases(
    db: Session,
    users: dict[str, User],
    data: dict[str, object],
) -> dict[str, Lease]:
    leases = {
        # Historical lease: Alice used to live in Cedar 101.
        "alice_old": Lease(
            unit_id=data["cedar_101"].id,
            tenant_user_id=users["alice"].id,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            rent_amount=1200,
            status=LeaseStatus.ENDED,
        ),

        # Bob currently occupies Cedar 101.
        "bob_active": Lease(
            unit_id=data["cedar_101"].id,
            tenant_user_id=users["bob"].id,
            start_date=date(2026, 1, 1),
            end_date=None,
            rent_amount=1350,
            status=LeaseStatus.ACTIVE,
        ),

        # Alice moved and kept the same User account.
        "alice_active": Lease(
            unit_id=data["harbor_a1"].id,
            tenant_user_id=users["alice"].id,
            start_date=date(2026, 1, 1),
            end_date=None,
            rent_amount=1500,
            status=LeaseStatus.ACTIVE,
        ),

        "carla_active": Lease(
            unit_id=data["pine_1a"].id,
            tenant_user_id=users["carla"].id,
            start_date=date(2026, 3, 1),
            end_date=None,
            rent_amount=1100,
            status=LeaseStatus.ACTIVE,
        ),

        "david_active": Lease(
            unit_id=data["garden_g1"].id,
            tenant_user_id=users["david"].id,
            start_date=date(2026, 2, 1),
            end_date=None,
            rent_amount=1250,
            status=LeaseStatus.ACTIVE,
        ),
    }

    db.add_all(leases.values())
    db.flush()

    return leases


def seed_expenses(
    db: Session,
    data: dict[str, object],
) -> None:
    expenses = [
        Expense(
            property_id=data["cedar"].id,
            unit_id=data["cedar_101"].id,
            amount=180,
            category="Plumbing",
            expense_date=date(2026, 3, 12),
            description="Repaired leaking sink connection.",
        ),
        Expense(
            property_id=data["cedar"].id,
            unit_id=data["cedar_101"].id,
            amount=225,
            category="Plumbing",
            expense_date=date(2026, 6, 8),
            description="Replaced worn sink valve and fittings.",
        ),
        Expense(
            property_id=data["cedar"].id,
            unit_id=data["cedar_101"].id,
            amount=290,
            category="Plumbing",
            expense_date=date(2026, 8, 21),
            description="Additional sink plumbing repair.",
        ),
        Expense(
            property_id=data["cedar"].id,
            unit_id=None,
            amount=650,
            category="Property",
            expense_date=date(2026, 7, 5),
            description="Annual common-area inspection and servicing.",
        ),
        Expense(
            property_id=data["harbor"].id,
            unit_id=data["harbor_a1"].id,
            amount=160,
            category="Electrical",
            expense_date=date(2026, 5, 16),
            description="Replaced damaged wall outlet.",
        ),
        Expense(
            property_id=data["pine"].id,
            unit_id=data["pine_1a"].id,
            amount=120,
            category="HVAC",
            expense_date=date(2026, 4, 11),
            description="Air conditioning filter and service.",
        ),
        Expense(
            property_id=data["garden"].id,
            unit_id=None,
            amount=430,
            category="Landscaping",
            expense_date=date(2026, 6, 20),
            description="Common garden maintenance.",
        ),
    ]

    db.add_all(expenses)


def seed_rent_obligations(
    db: Session,
    leases: dict[str, Lease],
) -> None:
    obligations = [
        RentObligation(
            lease_id=leases["bob_active"].id,
            amount=1350,
            due_date=date(2026, 9, 1),
            status=RentObligationStatus.PENDING,
        ),
        RentObligation(
            lease_id=leases["bob_active"].id,
            amount=1350,
            due_date=date(2026, 10, 1),
            status=RentObligationStatus.PENDING,
        ),
        RentObligation(
            lease_id=leases["alice_active"].id,
            amount=1500,
            due_date=date(2026, 10, 1),
            status=RentObligationStatus.PENDING,
        ),
        RentObligation(
            lease_id=leases["carla_active"].id,
            amount=1100,
            due_date=date(2026, 10, 1),
            status=RentObligationStatus.PENDING,
        ),
        RentObligation(
            lease_id=leases["david_active"].id,
            amount=1250,
            due_date=date(2026, 10, 1),
            status=RentObligationStatus.PENDING,
        ),
    ]

    db.add_all(obligations)

def seed_maintenance(
    db: Session,
    users: dict[str, User],
    data: dict[str, object],
) -> None:
    maintenance_records = [
        Maintenance(
            unit_id=data["cedar_101"].id,
            created_by_user_id=users["bob"].id,
            category="Plumbing",
            description=(
                "Kitchen sink is leaking underneath the cabinet."
            ),
            status=MaintenanceStatus.OPEN,
        ),
        Maintenance(
            unit_id=data["cedar_101"].id,
            created_by_user_id=users["bob"].id,
            category="Plumbing",
            description=(
                "Sink drain connection required another repair."
            ),
            status=MaintenanceStatus.RESOLVED,
        ),
        Maintenance(
            unit_id=data["harbor_a1"].id,
            created_by_user_id=users["alice"].id,
            category="Electrical",
            description=(
                "Bedroom wall outlet intermittently loses power."
            ),
            status=MaintenanceStatus.IN_PROGRESS,
        ),
        Maintenance(
            unit_id=data["pine_1a"].id,
            created_by_user_id=users["carla"].id,
            category="HVAC",
            description=(
                "Air conditioning airflow is weaker than usual."
            ),
            status=MaintenanceStatus.ASSIGNED,
        ),
    ]

    db.add_all(maintenance_records)


def seed_database() -> None:
    db = SessionLocal()

    try:
        print("Clearing existing development data...")
        clear_existing_data(db)

        print("Creating demo users...")
        users = seed_users(db)

        print("Creating properties, buildings, and units...")
        data = seed_properties_and_units(
            db,
            users,
        )

        print("Creating historical and active leases...")
        leases = seed_leases(
            db,
            users,
            data,
        )

        print("Creating maintenance records...")
        seed_maintenance(
           db,
           users,
           data,
        )

        print("Creating expenses...")
        seed_expenses(
            db,
            data,
        )

        print("Creating rent obligations...")
        seed_rent_obligations(
            db,
            leases,
        )

        db.commit()

        print()
        print("PropertyOps development database seeded successfully.")
        print()
        print("Demo accounts:")
        print("OWNER  owner.a@propertyops.dev / StrongPass123!")
        print("OWNER  owner.b@propertyops.dev / StrongPass456!")
        print("TENANT alice@propertyops.dev   / TenantPass123!")
        print("TENANT bob@propertyops.dev     / TenantPass456!")
        print("TENANT carla@propertyops.dev   / TenantPass789!")
        print("TENANT david@propertyops.dev   / TenantPass321!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()