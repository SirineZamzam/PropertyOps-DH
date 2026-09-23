"""add admin role

Revision ID: 69f91d378582
Revises: 16ce0e2f6cd4
Create Date: 2026-09-23 10:28:31.209461

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69f91d378582'
down_revision: Union[str, Sequence[str], None] = '16ce0e2f6cd4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TYPE user_role
        ADD VALUE IF NOT EXISTS 'ADMIN'
        """
    )


def downgrade() -> None:
    # PostgreSQL enum values cannot be safely removed
    # in-place without rebuilding the enum type.
    # Keep downgrade non-destructive.
    pass