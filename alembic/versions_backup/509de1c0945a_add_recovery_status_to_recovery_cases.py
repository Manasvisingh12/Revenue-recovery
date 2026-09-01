"""add recovery status to recovery cases

Revision ID: YOUR_GENERATED_REVISION
Revises: 8c0ebfc92862
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "509de1c0945a"
down_revision: Union[str, Sequence[str], None] = "8c0ebfc92862"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Phase 5 recovery status to recovery cases."""

    op.add_column(
        "recovery_cases",
        sa.Column(
            "recovery_status",
            sa.String(),
            nullable=False,
            server_default="AT_RISK",
        ),
    )

    op.create_index(
        "ix_recovery_cases_recovery_status",
        "recovery_cases",
        ["recovery_status"],
        unique=False,
    )


def downgrade() -> None:
    """Remove Phase 5 recovery status."""

    op.drop_index(
        "ix_recovery_cases_recovery_status",
        table_name="recovery_cases",
    )

    op.drop_column(
        "recovery_cases",
        "recovery_status",
    )