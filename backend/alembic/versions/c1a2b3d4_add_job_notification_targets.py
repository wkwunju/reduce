"""Add job notification targets mapping table

Revision ID: c1a2b3d4
Revises: 8c2d7a4f
Create Date: 2025-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1a2b3d4'
down_revision: Union[str, Sequence[str], None] = '8c2d7a4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("job_notification_targets"):
        op.create_table(
            'job_notification_targets',
            sa.Column('job_id', sa.Integer(), nullable=False),
            sa.Column('notification_target_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
            sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['notification_target_id'], ['notification_targets.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('job_id', 'notification_target_id')
        )
        op.create_index(op.f('ix_job_notification_targets_job_id'), 'job_notification_targets', ['job_id'], unique=False)
        op.create_index(op.f('ix_job_notification_targets_notification_target_id'), 'job_notification_targets', ['notification_target_id'], unique=False)
    else:
        op.execute("CREATE INDEX IF NOT EXISTS ix_job_notification_targets_job_id ON job_notification_targets (job_id)")
        op.execute("CREATE INDEX IF NOT EXISTS ix_job_notification_targets_notification_target_id ON job_notification_targets (notification_target_id)")

    op.execute("""
        INSERT INTO job_notification_targets (job_id, notification_target_id)
        SELECT jobs.id, jobs.notification_target_id
        FROM jobs
        WHERE jobs.notification_target_id IS NOT NULL
          AND NOT EXISTS (
            SELECT 1
            FROM job_notification_targets jnt
            WHERE jnt.job_id = jobs.id
              AND jnt.notification_target_id = jobs.notification_target_id
          )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_job_notification_targets_notification_target_id'), table_name='job_notification_targets')
    op.drop_index(op.f('ix_job_notification_targets_job_id'), table_name='job_notification_targets')
    op.drop_table('job_notification_targets')
