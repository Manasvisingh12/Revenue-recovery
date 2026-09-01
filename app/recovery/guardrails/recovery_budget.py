from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import RecoveryBudget


DEFAULT_DAILY_BUDGET = 10000


ACTION_COSTS = {

    "RETRY": 10,

    "WAIT": 0,

    "MESSAGE": 5,

    "ESCALATE": 100,

    "NO_ACTION": 0,

    "STOP": 0
}


def get_action_cost(
    action: str
) -> float:

    return ACTION_COSTS.get(
        action,
        0
    )


def get_or_create_budget(
    db: Session,
    merchant_id: str
):

    today = (
        datetime.now(
            timezone.utc
        ).date()
    )

    budget = (
        db.query(
            RecoveryBudget
        )
        .filter(
            RecoveryBudget.merchant_id
            == merchant_id,

            RecoveryBudget.budget_date
            == today
        )
        .first()
    )

    if budget:

        return budget

    budget = RecoveryBudget(
        merchant_id=merchant_id,

        budget_date=today,

        daily_limit=
            DEFAULT_DAILY_BUDGET,

        spent=0
    )

    db.add(
        budget
    )

    db.flush()

    return budget


def check_recovery_budget(
    db: Session,
    case
) -> dict:

    action = (
        case.recommended_action
    )

    action_cost = (
        get_action_cost(
            action
        )
    )

    budget = (
        get_or_create_budget(
            db,
            case.merchant_id
        )
    )

    projected_spend = (
        budget.spent
        + action_cost
    )

    if (
        projected_spend
        > budget.daily_limit
    ):

        return {
            "allowed": False,

            "reason":
                "Recovery budget exceeded.",

            "action_cost":
                action_cost,

            "budget_remaining":
                budget.daily_limit
                - budget.spent
        }

    return {
        "allowed": True,

        "reason":
            "Recovery budget is available.",

        "action_cost":
            action_cost,

        "budget_remaining":
            budget.daily_limit
            - projected_spend
    }


def consume_recovery_budget(
    db: Session,
    case
):

    budget = (
        get_or_create_budget(
            db,
            case.merchant_id
        )
    )

    cost = (
        get_action_cost(
            case.recommended_action
        )
    )

    budget.spent += cost