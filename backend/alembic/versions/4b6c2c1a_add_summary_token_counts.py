"""Add token counts to summaries

Revision ID: 4b6c2c1a
Revises: dbfeb162846a
Create Date: 2025-01-10 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b6c2c1a'
down_revision: Union[str, Sequence[str], None] = 'dbfeb162846a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('summaries', sa.Column('input_tokens', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('summaries', sa.Column('output_tokens', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('summaries', 'output_tokens')
    op.drop_column('summaries', 'input_tokens')
