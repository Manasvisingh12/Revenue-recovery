"""add incident intelligence to recovery cases

Revision ID: 7692006978e6
Revises: e04dd6f97538
Create Date: 2026-08-29 10:53:06.074540

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7692006978e6'
down_revision: Union[str, Sequence[str], None] = 'e04dd6f97538'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        'recovery_cases',
        sa.Column(
            'incident_type',
            sa.String(),
            nullable=True
        )
    )

    op.add_column(
        'recovery_cases',
        sa.Column(
            'incident_provider',
            sa.String(),
            nullable=True
        )
    )

    op.add_column(
        'recovery_cases',
        sa.Column(
            'incident_detected',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        )
    )

    op.alter_column(
        'recovery_cases',
        'incident_detected',
        server_default=None
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        'recovery_cases',
        'incident_detected'
    )

    op.drop_column(
        'recovery_cases',
        'incident_provider'
    )

    op.drop_column(
        'recovery_cases',
        'incident_type'
    )