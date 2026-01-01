"""Add notification targets and bind tokens

Revision ID: 8c2d7a4f
Revises: 6f3b1a2c
Create Date: 2025-01-10 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c2d7a4f'
down_revision: Union[str, Sequence[str], None] = '6f3b1a2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'notification_targets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('channel', sa.Enum('telegram', 'email', name='notificationchannel'), nullable=False),
        sa.Column('destination', sa.String(length=255), nullable=False),
        sa.Column('meta', sa.JSON(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_targets_id'), 'notification_targets', ['id'], unique=False)
    op.create_index(op.f('ix_notification_targets_user_id'), 'notification_targets', ['user_id'], unique=False)
    op.create_index(op.f('ix_notification_targets_channel'), 'notification_targets', ['channel'], unique=False)

    op.create_table(
        'notification_bind_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('channel', sa.Enum('telegram', 'email', name='notificationchannel'), nullable=False),
        sa.Column('token', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_bind_tokens_id'), 'notification_bind_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_notification_bind_tokens_user_id'), 'notification_bind_tokens', ['user_id'], unique=False)
    op.create_index(op.f('ix_notification_bind_tokens_channel'), 'notification_bind_tokens', ['channel'], unique=False)
    op.create_index(op.f('ix_notification_bind_tokens_token'), 'notification_bind_tokens', ['token'], unique=True)

    op.add_column('jobs', sa.Column('notification_target_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_jobs_notification_target_id'), 'jobs', ['notification_target_id'], unique=False)
    op.create_foreign_key(
        None,
        'jobs',
        'notification_targets',
        ['notification_target_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """Downgrade schema."""
    is_sqlite = op.get_bind().dialect.name == "sqlite"

    op.drop_constraint(None, 'jobs', type_='foreignkey')
    op.drop_index(op.f('ix_jobs_notification_target_id'), table_name='jobs')
    op.drop_column('jobs', 'notification_target_id')

    op.drop_index(op.f('ix_notification_bind_tokens_token'), table_name='notification_bind_tokens')
    op.drop_index(op.f('ix_notification_bind_tokens_channel'), table_name='notification_bind_tokens')
    op.drop_index(op.f('ix_notification_bind_tokens_user_id'), table_name='notification_bind_tokens')
    op.drop_index(op.f('ix_notification_bind_tokens_id'), table_name='notification_bind_tokens')
    op.drop_table('notification_bind_tokens')

    op.drop_index(op.f('ix_notification_targets_channel'), table_name='notification_targets')
    op.drop_index(op.f('ix_notification_targets_user_id'), table_name='notification_targets')
    op.drop_index(op.f('ix_notification_targets_id'), table_name='notification_targets')
    op.drop_table('notification_targets')

    if not is_sqlite:
        op.execute("""
        DO $$
        BEGIN
            DROP TYPE notificationchannel;
        EXCEPTION
            WHEN undefined_object THEN NULL;
        END$$;
        """)
