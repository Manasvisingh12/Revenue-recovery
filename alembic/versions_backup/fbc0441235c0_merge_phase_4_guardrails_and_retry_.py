"""merge phase 4 guardrails and retry limits

Revision ID: fbc0441235c0
Revises: 327442a4cc26, 96c75d0b4c81
Create Date: 2026-08-29 19:09:12.276137

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fbc0441235c0'
down_revision: Union[str, Sequence[str], None] = ('327442a4cc26', '96c75d0b4c81')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
