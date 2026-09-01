"""add retry limits

Revision ID: xxxxxxxxxxxx
Revises: 7692006978e6
Create Date: 2026-08-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "327442a4cc26"

down_revision: Union[
    str,
    Sequence[str],
    None
] = "7692006978e6"

branch_labels = None
depends_on = None


def upgrade() -> None:

    op.add_column(
        "recovery_cases",
        sa.Column(
            "retry_count",
            sa.Integer(),
            nullable=False,
            server_default="0"
        )
    )

    op.add_column(
        "recovery_cases",
        sa.Column(
            "max_retries",
            sa.Integer(),
            nullable=False,
            server_default="3"
        )
    )

    op.alter_column(
        "recovery_cases",
        "retry_count",
        server_default=None
    )

    op.alter_column(
        "recovery_cases",
        "max_retries",
        server_default=None
    )


def downgrade() -> None:

    op.drop_column(
        "recovery_cases",
        "max_retries"
    )

    op.drop_column(
        "recovery_cases",
        "retry_count"
    )