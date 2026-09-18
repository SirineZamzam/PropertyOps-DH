"""add unit type

Revision ID: 67d39e226ced
Revises: d8e4b91aa377
Create Date: 2026-09-18

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "67d39e226ced"
down_revision: Union[str, Sequence[str], None] = "d8e4b91aa377"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


unit_type_enum = postgresql.ENUM(
    "APARTMENT",
    "OFFICE",
    "RETAIL",
    "STORAGE",
    "OTHER",
    name="unit_type",
)


def upgrade() -> None:
    bind = op.get_bind()

    # PostgreSQL needs the enum type
    # created before the column uses it.
    unit_type_enum.create(
        bind,
        checkfirst=True,
    )

    op.add_column(
        "units",
        sa.Column(
            "unit_type",
            unit_type_enum,
            nullable=False,
            server_default="APARTMENT",
        ),
    )


def downgrade() -> None:
    bind = op.get_bind()

    op.drop_column(
        "units",
        "unit_type",
    )

    unit_type_enum.drop(
        bind,
        checkfirst=True,
    )