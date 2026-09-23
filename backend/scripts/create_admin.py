import argparse

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal

# Load the complete SQLAlchemy model registry before
# the first ORM query. Several models use string-based
# relationship names such as "Property".
from app.models.ai_analysis_job import AIAnalysisJob  # noqa: F401
from app.models.ai_insight import AIInsight  # noqa: F401
from app.models.ai_insight_evidence import AIInsightEvidence  # noqa: F401
from app.models.building import Building  # noqa: F401
from app.models.expense import Expense  # noqa: F401
from app.models.lease import Lease  # noqa: F401
from app.models.maintenance import Maintenance  # noqa: F401
from app.models.payment import Payment  # noqa: F401
from app.models.property import Property  # noqa: F401
from app.models.rent_obligation import RentObligation  # noqa: F401
from app.models.stripe_event import StripeEvent  # noqa: F401
from app.models.unit import Unit  # noqa: F401

from app.models.user import (
    User,
    UserRole,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Create the single "
            "PropertyOps admin account."
        )
    )

    parser.add_argument(
        "--email",
        required=True,
    )

    parser.add_argument(
        "--password",
        required=True,
    )

    parser.add_argument(
        "--first-name",
        required=True,
    )

    parser.add_argument(
        "--last-name",
        required=True,
    )

    return parser.parse_args()


def main():
    args = parse_args()

    normalized_email = (
        args.email
        .strip()
        .lower()
    )

    if len(
        args.password
    ) < 12:
        raise SystemExit(
            "Admin password must "
            "be at least 12 characters."
        )

    with SessionLocal() as db:
        existing = db.scalar(
            select(User).where(
                User.email
                == normalized_email
            )
        )

        if existing is not None:
            raise SystemExit(
                "A user with this "
                "email already exists."
            )

        existing_admin = db.scalar(
            select(User).where(
                User.role
                == UserRole.ADMIN
            )
        )

        if existing_admin is not None:
            raise SystemExit(
                "An admin account "
                "already exists."
            )

        admin = User(
            first_name=(
                args.first_name
                .strip()
            ),
            last_name=(
                args.last_name
                .strip()
            ),
            email=(
                normalized_email
            ),
            password_hash=(
                hash_password(
                    args.password
                )
            ),
            role=UserRole.ADMIN,
            is_active=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(
            "Admin account created:"
        )

        print(
            f"  ID: {admin.id}"
        )

        print(
            f"  Email: {admin.email}"
        )


if __name__ == "__main__":
    main()