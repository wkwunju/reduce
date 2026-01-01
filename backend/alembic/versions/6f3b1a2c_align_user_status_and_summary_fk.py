"""Align users.status enum and add summary execution FK

Revision ID: 6f3b1a2c
Revises: 4b6c2c1a
Create Date: 2025-01-10 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f3b1a2c'
down_revision: Union[str, Sequence[str], None] = '4b6c2c1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    if op.get_bind().dialect.name == "sqlite":
        return
    op.execute("""
    DO $$
    BEGIN
        CREATE TYPE userstatus AS ENUM ('UNVERIFIED', 'ACTIVE', 'SUSPENDED');
    EXCEPTION
        WHEN duplicate_object THEN NULL;
    END$$;
    """)

    op.execute("""
    UPDATE users
    SET status = 'ACTIVE'
    WHERE status IS NULL;
    """)

    op.execute("""
    ALTER TABLE users
    ALTER COLUMN status DROP DEFAULT;
    """)

    op.execute("""
    ALTER TABLE users
    ALTER COLUMN status TYPE userstatus
    USING (
        CASE
            WHEN status ILIKE 'unverified' THEN 'UNVERIFIED'
            WHEN status ILIKE 'suspended' THEN 'SUSPENDED'
            WHEN status ILIKE 'active' THEN 'ACTIVE'
            ELSE 'ACTIVE'
        END
    )::userstatus;
    """)

    op.execute("""
    ALTER TABLE users
    ALTER COLUMN status SET DEFAULT 'UNVERIFIED';
    """)

    op.execute("""
    ALTER TABLE users
    ALTER COLUMN status SET NOT NULL;
    """)

    op.create_foreign_key(
        'summaries_execution_id_fkey',
        'summaries',
        'job_executions',
        ['execution_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """Downgrade schema."""
    if op.get_bind().dialect.name == "sqlite":
        return
    op.drop_constraint('summaries_execution_id_fkey', 'summaries', type_='foreignkey')

    op.execute("""
    ALTER TABLE users
    ALTER COLUMN status DROP DEFAULT;
    """)

    op.execute("""
    ALTER TABLE users
    ALTER COLUMN status DROP NOT NULL;
    """)

    op.execute("""
    ALTER TABLE users
    ALTER COLUMN status TYPE varchar(20)
    USING lower(status::text);
    """)

    op.execute("""
    ALTER TABLE users
    ALTER COLUMN status SET DEFAULT 'active';
    """)

    op.execute("""
    DO $$
    BEGIN
        DROP TYPE userstatus;
    EXCEPTION
        WHEN undefined_object THEN NULL;
    END$$;
    """)
