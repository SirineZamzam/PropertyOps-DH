"""add stripe subscription billing

Revision ID: bddb16181ad9
Revises: 942bbeb0aa1c
Create Date: 2026-09-23 13:00:45.543973

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'bddb16181ad9'
down_revision: Union[str, Sequence[str], None] = '942bbeb0aa1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    billing_interval = postgresql.ENUM(
        "MONTHLY",
        "YEARLY",
        name="billing_interval",
        create_type=False,
    )

    billing_interval.create(
        op.get_bind(),
        checkfirst=True,
    )

    subscription_payment_status = postgresql.ENUM(
        "PAID",
        "FAILED",
        name="subscription_payment_status",
        create_type=False,
    )

    subscription_payment_status.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.add_column(
        "owner_subscriptions",
        sa.Column(
            "billing_interval",
            billing_interval,
            nullable=True,
        ),
    )

    op.add_column(
        "owner_subscriptions",
        sa.Column(
            "stripe_customer_id",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "owner_subscriptions",
        sa.Column(
            "stripe_subscription_id",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "owner_subscriptions",
        sa.Column(
            "current_period_end",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "owner_subscriptions",
        sa.Column(
            "cancel_at_period_end",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.create_index(
        "ix_owner_subscriptions_stripe_customer_id",
        "owner_subscriptions",
        ["stripe_customer_id"],
        unique=True,
    )

    op.create_index(
        "ix_owner_subscriptions_stripe_subscription_id",
        "owner_subscriptions",
        ["stripe_subscription_id"],
        unique=True,
    )

    op.create_table(
        "subscription_payments",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),

        sa.Column(
            "owner_subscription_id",
            sa.Integer(),
            nullable=False,
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
            "stripe_invoice_id",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "amount",
            sa.Numeric(10, 2),
            nullable=False,
        ),

        sa.Column(
            "currency",
            sa.String(length=12),
            nullable=False,
        ),

        sa.Column(
            "status",
            subscription_payment_status,
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),

        sa.ForeignKeyConstraint(
            ["owner_subscription_id"],
            ["owner_subscriptions.id"],
            name=(
                "fk_subscription_payments_"
                "owner_subscription_id"
            ),
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            name=(
                "fk_subscription_payments_owner_id"
            ),
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["subscription_plans.id"],
            name=(
                "fk_subscription_payments_plan_id"
            ),
        ),

        sa.UniqueConstraint(
            "stripe_invoice_id",
            name=(
                "uq_subscription_payments_"
                "stripe_invoice_id"
            ),
        ),
    )

    op.create_index(
        "ix_subscription_payments_owner_subscription_id",
        "subscription_payments",
        ["owner_subscription_id"],
        unique=False,
    )

    op.create_index(
        "ix_subscription_payments_owner_id",
        "subscription_payments",
        ["owner_id"],
        unique=False,
    )

    op.create_index(
        "ix_subscription_payments_plan_id",
        "subscription_payments",
        ["plan_id"],
        unique=False,
    )

    op.create_index(
        "ix_subscription_payments_stripe_invoice_id",
        "subscription_payments",
        ["stripe_invoice_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_subscription_payments_stripe_invoice_id",
        table_name="subscription_payments",
    )

    op.drop_index(
        "ix_subscription_payments_plan_id",
        table_name="subscription_payments",
    )

    op.drop_index(
        "ix_subscription_payments_owner_id",
        table_name="subscription_payments",
    )

    op.drop_index(
        "ix_subscription_payments_owner_subscription_id",
        table_name="subscription_payments",
    )

    op.drop_table(
        "subscription_payments"
    )

    op.drop_index(
        "ix_owner_subscriptions_stripe_subscription_id",
        table_name="owner_subscriptions",
    )

    op.drop_index(
        "ix_owner_subscriptions_stripe_customer_id",
        table_name="owner_subscriptions",
    )

    op.drop_column(
        "owner_subscriptions",
        "cancel_at_period_end",
    )

    op.drop_column(
        "owner_subscriptions",
        "current_period_end",
    )

    op.drop_column(
        "owner_subscriptions",
        "stripe_subscription_id",
    )

    op.drop_column(
        "owner_subscriptions",
        "stripe_customer_id",
    )

    op.drop_column(
        "owner_subscriptions",
        "billing_interval",
    )

    subscription_payment_status = postgresql.ENUM(
        "PAID",
        "FAILED",
        name="subscription_payment_status",
        create_type=False,
    )

    subscription_payment_status.drop(
        op.get_bind(),
        checkfirst=True,
    )

    billing_interval = postgresql.ENUM(
        "MONTHLY",
        "YEARLY",
        name="billing_interval",
        create_type=False,
    )

    billing_interval.drop(
        op.get_bind(),
        checkfirst=True,
    )