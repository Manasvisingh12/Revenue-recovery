"""add phase 4 guardrails

Revision ID: 96c75d0b4c81
Revises: 917a9bb3fabe
Create Date: 2026-08-29 16:33:53.604349

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96c75d0b4c81'
down_revision: Union[str, Sequence[str], None] = '917a9bb3fabe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ---------------------------------
    # RECOVERY CASE FIELDS
    # ---------------------------------

    op.add_column(
        "recovery_cases",
        sa.Column(
            "customer_consent",
            sa.Boolean(),
            nullable=True
        )
    )

    op.add_column(
        "recovery_cases",
        sa.Column(
            "recovered",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        )
    )

    op.add_column(
        "recovery_cases",
        sa.Column(
            "recovered_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=True
        )
    )

    op.add_column(
        "recovery_cases",
        sa.Column(
            "execution_status",
            sa.String(),
            nullable=False,
            server_default="PENDING"
        )
    )

    op.alter_column(
        "recovery_cases",
        "recovered",
        server_default=None
    )

    op.alter_column(
        "recovery_cases",
        "execution_status",
        server_default=None
    )

    # ---------------------------------
    # ACTION LOG
    # ---------------------------------

    op.create_table(
        "recovery_action_logs",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True
        ),

        sa.Column(
            "case_id",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "merchant_id",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "customer_id",
            sa.String(),
            nullable=True
        ),

        sa.Column(
            "action",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "status",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "block_reason",
            sa.String(),
            nullable=True
        ),

        sa.Column(
            "estimated_cost",
            sa.Float(),
            nullable=False,
            server_default="0"
        ),

        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True
            ),
            server_default=sa.func.now()
        )
    )

    # ---------------------------------
    # CIRCUIT BREAKER
    # ---------------------------------

    op.create_table(
        "circuit_breaker_states",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True
        ),

        sa.Column(
            "provider",
            sa.String(),
            nullable=False,
            unique=True
        ),

        sa.Column(
            "state",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "failure_count",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "failure_threshold",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "opened_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=True
        ),

        sa.Column(
            "cooldown_seconds",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(
                timezone=True
            ),
            server_default=sa.func.now()
        )
    )

    # ---------------------------------
    # RECOVERY BUDGET
    # ---------------------------------

    op.create_table(
        "recovery_budgets",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True
        ),

        sa.Column(
            "merchant_id",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "budget_date",
            sa.Date(),
            nullable=False
        ),

        sa.Column(
            "daily_limit",
            sa.Float(),
            nullable=False
        ),

        sa.Column(
            "spent",
            sa.Float(),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True
            ),
            server_default=sa.func.now()
        )
    )

    # ---------------------------------
    # INDEXES
    # ---------------------------------

    op.create_index(
        "ix_recovery_cases_recovered",
        "recovery_cases",
        ["recovered"]
    )

    op.create_index(
        "ix_recovery_cases_execution_status",
        "recovery_cases",
        ["execution_status"]
    )


def downgrade() -> None:

    op.drop_index(
        "ix_recovery_cases_execution_status",
        table_name="recovery_cases"
    )

    op.drop_index(
        "ix_recovery_cases_recovered",
        table_name="recovery_cases"
    )

    op.drop_table(
        "recovery_budgets"
    )

    op.drop_table(
        "circuit_breaker_states"
    )

    op.drop_table(
        "recovery_action_logs"
    )

    op.drop_column(
        "recovery_cases",
        "execution_status"
    )

    op.drop_column(
        "recovery_cases",
        "recovered_at"
    )

    op.drop_column(
        "recovery_cases",
        "recovered"
    )

    op.drop_column(
        "recovery_cases",
        "customer_consent"
    )
