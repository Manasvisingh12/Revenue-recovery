"""add recovery intelligence fields

Revision ID: 917a9bb3fabe
Revises: 7692006978e6
Create Date: 2026-08-29 16:19:20.379609

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '917a9bb3fabe'
down_revision: Union[str, Sequence[str], None] = '7692006978e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "recovery_cases",
        sa.Column(
            "opportunity_score",
            sa.Float(),
            nullable=True
        )
    )

    op.add_column(
        "recovery_cases",
        sa.Column(
            "recovery_probability",
            sa.Float(),
            nullable=True
        )
    )

    op.add_column(
        "recovery_cases",
        sa.Column(
            "expected_recovery_value",
            sa.Float(),
            nullable=True
        )
    )

    op.add_column(
        "recovery_cases",
        sa.Column(
            "ai_diagnosis",
            sa.String(),
            nullable=True
        )
    )

    op.add_column(
        "recovery_cases",
        sa.Column(
            "ai_confidence",
            sa.Float(),
            nullable=True
        )
    )

    op.add_column(
        "recovery_cases",
        sa.Column(
            "action_reason",
            sa.String(),
            nullable=True
        )
    )

    op.add_column(
        "recovery_cases",
        sa.Column(
            "priority",
            sa.String(),
            nullable=True
        )
    )

    op.add_column(
        "recovery_cases",
        sa.Column(
            "intelligence_status",
            sa.String(),
            nullable=False,
            server_default="PENDING"
        )
    )

    op.alter_column(
        "recovery_cases",
        "intelligence_status",
        server_default=None
    )

    op.create_index(
        "ix_recovery_cases_opportunity_score",
        "recovery_cases",
        ["opportunity_score"]
    )

    op.create_index(
        "ix_recovery_cases_priority",
        "recovery_cases",
        ["priority"]
    )

    op.create_index(
        "ix_recovery_cases_intelligence_status",
        "recovery_cases",
        ["intelligence_status"]
    )


def downgrade() -> None:

    op.drop_index(
        "ix_recovery_cases_intelligence_status",
        table_name="recovery_cases"
    )

    op.drop_index(
        "ix_recovery_cases_priority",
        table_name="recovery_cases"
    )

    op.drop_index(
        "ix_recovery_cases_opportunity_score",
        table_name="recovery_cases"
    )

    op.drop_column(
        "recovery_cases",
        "intelligence_status"
    )

    op.drop_column(
        "recovery_cases",
        "priority"
    )

    op.drop_column(
        "recovery_cases",
        "action_reason"
    )

    op.drop_column(
        "recovery_cases",
        "ai_confidence"
    )

    op.drop_column(
        "recovery_cases",
        "ai_diagnosis"
    )

    op.drop_column(
        "recovery_cases",
        "expected_recovery_value"
    )

    op.drop_column(
        "recovery_cases",
        "recovery_probability"
    )

    op.drop_column(
        "recovery_cases",
        "opportunity_score"
    )