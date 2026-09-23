"""add subscription plans and owner subscriptions

Revision ID: 942bbeb0aa1c
Revises: 69f91d378582
Create Date: 2026-09-23

"""

from typing import (
    Sequence,
    Union,
)

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import (
    postgresql,
)


# revision identifiers,
# used by Alembic.
revision: str = (
    "942bbeb0aa1c"
)

down_revision: (
    Union[
        str,
        Sequence[str],
        None,
    ]
) = "69f91d378582"

branch_labels: (
    Union[
        str,
        Sequence[str],
        None,
    ]
) = None

depends_on: (
    Union[
        str,
        Sequence[str],
        None,
    ]
) = None


def upgrade() -> None:
    subscription_status = (
        postgresql.ENUM(
            "FREE",
            "ACTIVE",
            "INCOMPLETE",
            "PAST_DUE",
            "CANCELED",
            name=(
                "subscription_status"
            ),

            # IMPORTANT:
            # We create the enum
            # ourselves below.
            create_type=False,
        )
    )

    subscription_status.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.create_table(
        "subscription_plans",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),

        sa.Column(
            "code",
            sa.String(
                length=50,
            ),
            nullable=False,
        ),

        sa.Column(
            "name",
            sa.String(
                length=100,
            ),
            nullable=False,
        ),

        sa.Column(
            "monthly_price",
            sa.Numeric(
                10,
                2,
            ),
            nullable=False,
        ),

        sa.Column(
            "yearly_price",
            sa.Numeric(
                10,
                2,
            ),
            nullable=False,
        ),

        sa.Column(
            "max_properties",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=(
                sa.true()
            ),
        ),

        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True,
            ),
            nullable=False,
            server_default=(
                sa.text(
                    "now()"
                )
            ),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(
                timezone=True,
            ),
            nullable=False,
            server_default=(
                sa.text(
                    "now()"
                )
            ),
        ),

        sa.UniqueConstraint(
            "code",
            name=(
                "uq_subscription_plans_code"
            ),
        ),
    )

    op.create_index(
        "ix_subscription_plans_code",
        "subscription_plans",
        ["code"],
        unique=False,
    )

    op.create_table(
        "owner_subscriptions",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),

        sa.Column(
            "owner_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "plan_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "status",
            subscription_status,
            nullable=False,
            server_default=(
                "FREE"
            ),
        ),

        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True,
            ),
            nullable=False,
            server_default=(
                sa.text(
                    "now()"
                )
            ),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(
                timezone=True,
            ),
            nullable=False,
            server_default=(
                sa.text(
                    "now()"
                )
            ),
        ),

        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            name=(
                "fk_owner_subscriptions_"
                "owner_id_users"
            ),
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["plan_id"],
            [
                "subscription_plans.id"
            ],
            name=(
                "fk_owner_subscriptions_"
                "plan_id_subscription_plans"
            ),
        ),

        sa.UniqueConstraint(
            "owner_id",
            name=(
                "uq_owner_subscriptions_"
                "owner_id"
            ),
        ),
    )

    op.create_index(
        (
            "ix_owner_subscriptions_"
            "owner_id"
        ),
        "owner_subscriptions",
        ["owner_id"],
        unique=False,
    )

    op.create_index(
        (
            "ix_owner_subscriptions_"
            "plan_id"
        ),
        "owner_subscriptions",
        ["plan_id"],
        unique=False,
    )

    op.execute(
        """
        INSERT INTO subscription_plans
            (
                code,
                name,
                monthly_price,
                yearly_price,
                max_properties,
                sort_order,
                is_active
            )
        VALUES
            (
                'FREE',
                'Free',
                0.00,
                0.00,
                2,
                10,
                TRUE
            ),
            (
                'STANDARD',
                'Standard',
                9.00,
                90.00,
                10,
                20,
                TRUE
            ),
            (
                'PRO',
                'Pro',
                19.00,
                190.00,
                NULL,
                30,
                TRUE
            )
        """
    )

    op.execute(
        """
        INSERT INTO owner_subscriptions
            (
                owner_id,
                plan_id,
                status
            )
        SELECT
            users.id,
            subscription_plans.id,
            'FREE'::subscription_status
        FROM users
        CROSS JOIN subscription_plans
        WHERE
            users.role = 'OWNER'
            AND subscription_plans.code = 'FREE'
        ON CONFLICT (owner_id)
        DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_index(
        (
            "ix_owner_subscriptions_"
            "plan_id"
        ),
        table_name=(
            "owner_subscriptions"
        ),
    )

    op.drop_index(
        (
            "ix_owner_subscriptions_"
            "owner_id"
        ),
        table_name=(
            "owner_subscriptions"
        ),
    )

    op.drop_table(
        "owner_subscriptions"
    )

    op.drop_index(
        (
            "ix_subscription_plans_"
            "code"
        ),
        table_name=(
            "subscription_plans"
        ),
    )

    op.drop_table(
        "subscription_plans"
    )

    subscription_status = (
        postgresql.ENUM(
            "FREE",
            "ACTIVE",
            "INCOMPLETE",
            "PAST_DUE",
            "CANCELED",
            name=(
                "subscription_status"
            ),
            create_type=False,
        )
    )

    subscription_status.drop(
        op.get_bind(),
        checkfirst=True,
    )