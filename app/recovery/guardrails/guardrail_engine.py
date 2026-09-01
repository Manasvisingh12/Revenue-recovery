
from sqlalchemy.orm import Session

from app.models import RecoveryCase

from app.recovery.guardrails.recovery_check import (
    check_already_recovered,
)

from app.recovery.guardrails.retry_guard import (
    check_retry_limit,
)

from app.recovery.guardrails.budget_guard import (
    check_recovery_budget,
)

from app.recovery.guardrails.contact_guard import (
    check_contact_limit,
)

from app.recovery.guardrails.circuit_breaker import (
    check_circuit_breaker,
)


def validate_recovery_action(
    db: Session,
    case: RecoveryCase,
    action: str
) -> dict:
    """
    Central Phase 4 guardrail validation.

    Phase 3 recommends an action.
    Phase 4 decides whether that action
    is safe to execute.
    """

    # ========================================================
    # 1. VALIDATE ACTION
    # ========================================================

    allowed_actions = {
        "RETRY",
        "WAIT",
        "MESSAGE",
        "ESCALATE",
        "NO_ACTION",
        "STOP"
    }

    if action not in allowed_actions:
        return {
            "allowed": False,
            "action": "STOP",
            "reason": "INVALID_ACTION"
        }

    # ========================================================
    # 2. ALREADY RECOVERED CHECK
    # ========================================================

    recovery_check = check_already_recovered(
        db,
        case
    )

    if not recovery_check["allowed"]:
        return {
            "allowed": False,
            "action": "NO_ACTION",
            "reason": recovery_check["reason"]
        }

    # ========================================================
    # 3. RETRY LIMIT
    # ========================================================

    if action == "RETRY":

        retry_check = check_retry_limit(
            case
        )

        if not retry_check["allowed"]:
            return {
                "allowed": False,
                "action": "ESCALATE",
                "reason": retry_check["reason"]
            }

    # ========================================================
    # 4. CONSENT CHECK
    # ========================================================

    if action == "MESSAGE":

        if case.customer_consent is False:
            return {
                "allowed": False,
                "action": "ESCALATE",
                "reason": "CUSTOMER_CONSENT_REQUIRED"
            }

    # ========================================================
    # 5. CONTACT LIMIT
    # ========================================================

    if action == "MESSAGE":

        contact_check = check_contact_limit(
            db,
            case
        )

        if not contact_check["allowed"]:
            return {
                "allowed": False,
                "action": "NO_ACTION",
                "reason": contact_check["reason"]
            }

    # ========================================================
    # 6. RECOVERY BUDGET
    # ========================================================

    estimated_cost = 0.0

    if action == "MESSAGE":
        estimated_cost = 5.0

    elif action == "RETRY":
        estimated_cost = 10.0

    budget_check = check_recovery_budget(
        db,
        case,
        estimated_cost
    )

    if not budget_check["allowed"]:
        return {
            "allowed": False,
            "action": "NO_ACTION",
            "reason": budget_check["reason"]
        }

    # ========================================================
    # 7. CIRCUIT BREAKER
    # ========================================================

    if action == "RETRY":

        circuit_check = check_circuit_breaker(
            db,
            case
        )

        if not circuit_check["allowed"]:
            return {
                "allowed": False,
                "action": "ESCALATE",
                "reason": circuit_check["reason"]
            }

    # ========================================================
    # 8. HUMAN ESCALATION
    # ========================================================

    if action == "ESCALATE":

        return {
            "allowed": True,
            "action": "ESCALATE",
            "reason": "HUMAN_ESCALATION_REQUIRED"
        }

    # ========================================================
    # 9. NO ACTION
    # ========================================================

    if action == "NO_ACTION":

        return {
            "allowed": True,
            "action": "NO_ACTION",
            "reason": "NO_ACTION_REQUIRED"
        }

    # ========================================================
    # 10. STOP
    # ========================================================

    if action == "STOP":

        return {
            "allowed": True,
            "action": "STOP",
            "reason": "ACTION_STOPPED_BY_POLICY"
        }

    # ========================================================
    # 11. EVERYTHING PASSED
    # ========================================================

    return {
        "allowed": True,
        "action": action,
        "reason": "ALL_GUARDRAILS_PASSED"
    }

