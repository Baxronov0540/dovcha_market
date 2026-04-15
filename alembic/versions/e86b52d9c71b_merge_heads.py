"""merge_heads

Revision ID: e86b52d9c71b
Revises: 0e13724cce5a, 3c8f9d5a2e1b
Create Date: 2026-04-15 09:58:52.213917

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e86b52d9c71b'
down_revision: Union[str, Sequence[str], None] = ('0e13724cce5a', '3c8f9d5a2e1b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
