"""Add language to jobs

Revision ID: d7e9f1a0
Revises: c1a2b3d4
Create Date: 2025-01-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7e9f1a0'
down_revision: Union[str, Sequence[str], None] = 'c1a2b3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('jobs', sa.Column('language', sa.String(length=20), nullable=False, server_default='en'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('jobs', 'language')
