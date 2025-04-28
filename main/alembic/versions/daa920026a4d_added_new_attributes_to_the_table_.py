"""added new attributes to the table recommendations

Revision ID: daa920026a4d
Revises: 493a20bd2d74
Create Date: 2025-04-28 11:52:20.979052

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'daa920026a4d'
down_revision: Union[str, None] = '493a20bd2d74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'recommendations',
        sa.Column(
            'is_accepted',
            sa.Boolean(),
            server_default=sa.text('False'),
            nullable=False
        )
    )
    op.add_column(
        'recommendations',
        sa.Column(
            'is_deleted',
            sa.Boolean(),
            server_default=sa.text('False'),
            nullable=False
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('recommendations', 'is_deleted')
    op.drop_column('recommendations', 'is_accepted')
