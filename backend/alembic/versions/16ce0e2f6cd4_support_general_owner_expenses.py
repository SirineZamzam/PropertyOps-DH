"""support general owner expenses

Revision ID: 16ce0e2f6cd4
Revises: 15154da1ea35
Create Date: 2026-09-22 23:05:15.895182

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '16ce0e2f6cd4'
down_revision: Union[str, Sequence[str], None] = '15154da1ea35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "expenses",
        sa.Column(
            "owner_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_expenses_owner_id_users",
        "expenses",
        "users",
        ["owner_id"],
        ["id"],
    )

    op.execute(
        """
        UPDATE expenses
        SET owner_id = properties.owner_id
        FROM properties
        WHERE expenses.property_id = properties.id
        """
    )

    op.alter_column(
        "expenses",
        "owner_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_index(
        "ix_expenses_owner_id",
        "expenses",
        ["owner_id"],
        unique=False,
    )

    op.alter_column(
        "expenses",
        "property_id",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM expenses
        WHERE property_id IS NULL
        """
    )

    op.alter_column(
        "expenses",
        "property_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.drop_index(
        "ix_expenses_owner_id",
        table_name="expenses",
    )

    op.drop_constraint(
        "fk_expenses_owner_id_users",
        "expenses",
        type_="foreignkey",
    )

    op.drop_column(
        "expenses",
        "owner_id",
    )