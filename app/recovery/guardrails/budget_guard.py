from datetime import date

from sqlalchemy.orm import Session

from app.models import (
    RecoveryCase,
    RecoveryBudget,
)


DEFAULT_DAILY_LIMIT = 10000.0


def check_recovery_budget(
    db: Session,
    case: RecoveryCase,
    estimated_cost: float
) -> dict:
    """
    Prevent recovery actions from exceeding
    the merchant's daily recovery budget.
    """

    today = date.today()

    budget = db.query(
        RecoveryBudget
    ).filter(
        RecoveryBudget.merchant_id
        == case.merchant_id,

        RecoveryBudget.budget_date
        == today
    ).first()

    if budget is None:

        budget = RecoveryBudget(
            merchant_id=case.merchant_id,
            budget_date=today,
            daily_limit=DEFAULT_DAILY_LIMIT,
            spent=0
        )

        db.add(budget)

        db.flush()

    if (
        budget.spent
        + estimated_cost
        > budget.daily_limit
    ):

        return {
            "allowed": False,
            "reason": "RECOVERY_BUDGET_EXCEEDED"
        }

    return {
        "allowed": True,
        "reason": None
    }