"""add payment method and manual payment metadata

Revision ID: 15154da1ea35
Revises: a04f091db3bb
Create Date: 2026-09-22 16:23:17.971811

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '15154da1ea35'
down_revision: Union[str, Sequence[str], None] = 'a04f091db3bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    payment_method = postgresql.ENUM(
        "STRIPE",
        "CASH",
        name="payment_method",
    )

    payment_method.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.add_column(
        "payments",
        sa.Column(
            "payment_method",
            payment_method,
            nullable=False,
            server_default="STRIPE",
        ),
    )

    op.add_column(
        "payments",
        sa.Column(
            "manual_note",
            sa.String(length=500),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "payments",
        "manual_note",
    )

    op.drop_column(
        "payments",
        "payment_method",
    )

    payment_method = postgresql.ENUM(
        "STRIPE",
        "CASH",
        name="payment_method",
    )

    payment_method.drop(
        op.get_bind(),
        checkfirst=True,
    )