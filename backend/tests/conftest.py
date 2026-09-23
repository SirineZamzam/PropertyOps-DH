import pytest

from fastapi.testclient import (
    TestClient,
)

from sqlalchemy import (
    create_engine,
    delete,
)

from sqlalchemy.orm import (
    Session,
    sessionmaker,
)

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app

from app.models.ai_analysis_job import (
    AIAnalysisJob,
)

from app.models.ai_insight import (
    AIInsight,
)

from app.models.ai_insight_evidence import (
    AIInsightEvidence,
)

from app.models.building import Building
from app.models.expense import Expense
from app.models.lease import Lease
from app.models.maintenance import Maintenance

from app.models.owner_subscription import (
    OwnerSubscription,
)

from app.models.payment import Payment
from app.models.property import Property

from app.models.rent_obligation import (
    RentObligation,
)

from app.models.stripe_event import (
    StripeEvent,
)

from app.models.subscription_payment import (
    SubscriptionPayment,
)

from app.models.subscription_plan import (
    SubscriptionPlan,
)

from app.models.unit import Unit
from app.models.user import User


test_engine = create_engine(
    settings.test_database_url,
    pool_pre_ping=True,
)


TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(
    scope="session",
    autouse=True,
)
def prepare_test_database():
    Base.metadata.drop_all(
        bind=test_engine
    )

    Base.metadata.create_all(
        bind=test_engine
    )

    yield

    Base.metadata.drop_all(
        bind=test_engine
    )


@pytest.fixture()
def db():
    session = (
        TestingSessionLocal()
    )

    try:
        yield session

    finally:
        session.rollback()

        # Delete children before
        # parents because of FKs.
        session.execute(
            delete(
                AIInsightEvidence
            )
        )

        session.execute(
            delete(
                AIInsight
            )
        )

        session.execute(
            delete(
                AIAnalysisJob
            )
        )

        session.execute(
            delete(
                StripeEvent
            )
        )

        session.execute(
            delete(
                Payment
            )
        )

        session.execute(
            delete(
                RentObligation
            )
        )

        session.execute(
            delete(
                Expense
            )
        )

        session.execute(
            delete(
                Maintenance
            )
        )

        session.execute(
            delete(
                Lease
            )
        )

        session.execute(
            delete(
                Unit
            )
        )

        session.execute(
            delete(
                Building
            )
        )

        session.execute(
            delete(
                Property
            )
        )

        session.execute(
            delete(
                SubscriptionPayment
            )
        )

        session.execute(
            delete(
                OwnerSubscription
            )
        )

        session.execute(
            delete(
                SubscriptionPlan
            )
        )

        session.execute(
            delete(
                User
            )
        )

        session.commit()
        session.close()


@pytest.fixture()
def client(
    db: Session,
):
    def override_get_db():
        yield db

    app.dependency_overrides[
        get_db
    ] = override_get_db

    with TestClient(
        app
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()