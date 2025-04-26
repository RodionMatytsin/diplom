"""added hash_password attribute to table users

Revision ID: 493a20bd2d74
Revises: ce9f19c6a96c
Create Date: 2025-04-26 13:49:25.500715

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '493a20bd2d74'
down_revision: Union[str, None] = 'ce9f19c6a96c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('hash_password', sa.String(length=255), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'hash_password')
