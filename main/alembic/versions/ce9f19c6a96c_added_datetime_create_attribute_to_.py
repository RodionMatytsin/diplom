"""added datetime_create attribute to table questions

Revision ID: ce9f19c6a96c
Revises: 76db3f0dedc2
Create Date: 2025-04-26 01:27:59.682637

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'ce9f19c6a96c'
down_revision: Union[str, None] = '76db3f0dedc2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'questions',
        sa.Column(
            'datetime_create',
            sa.DateTime(),
            server_default=sa.text("(now() AT TIME ZONE 'Asia/Novosibirsk')"),
            nullable=False
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('questions', 'datetime_create')
