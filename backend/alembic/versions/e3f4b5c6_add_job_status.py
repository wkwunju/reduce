"""Add status to jobs

Revision ID: e3f4b5c6
Revises: d7e9f1a0
Create Date: 2025-01-15 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3f4b5c6'
down_revision: Union[str, Sequence[str], None] = 'd7e9f1a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"
    jobstatus_enum = sa.Enum('active', 'deleted', name='jobstatus')
    if is_postgres:
        jobstatus_enum.create(bind, checkfirst=True)
    op.add_column(
        'jobs',
        sa.Column(
            'status',
            jobstatus_enum,
            nullable=False,
            server_default='active'
        )
    )
    op.create_index(op.f('ix_jobs_status'), 'jobs', ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"
    op.drop_index(op.f('ix_jobs_status'), table_name='jobs')
    op.drop_column('jobs', 'status')
    if is_postgres:
        sa.Enum(name='jobstatus').drop(bind, checkfirst=True)
