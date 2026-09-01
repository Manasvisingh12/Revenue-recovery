from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import (
    RecoveryCase,
    RecoveryOutcome,
)


# ============================================================
# PHASE 5 — RECOVERY OUTCOME TRACKER
# ============================================================


def track_recovery_outcome(
    db: Session,
    case: RecoveryCase,
    execution_result: dict
) -> dict:
    """
    Persist a recovery execution result.

    Updates the RecoveryOutcome record and
    transitions the RecoveryCase when revenue
    is successfully recovered.
    """

    status = execution_result.get(
        "status",
        "FAILED"
    )

    recovered_amount = execution_result.get(
        "recovered_amount",
        0
    )

    # ========================================================
    # CREATE OUTCOME RECORD
    # ========================================================

    outcome = RecoveryOutcome(
        case_id=case.case_id,
        merchant_id=case.merchant_id,
        payment_id=case.payment_id,
        checkout_id=case.checkout_id,
        action=execution_result.get(
            "action",
            case.recommended_action
        ),
        status=status,
        amount=case.amount,
        recovered_amount=recovered_amount,
        failure_reason=execution_result.get(
            "failure_reason"
        ),
        payment_link=execution_result.get(
            "payment_link"
        ),
        message_status=execution_result.get(
            "message_status"
        ),
        outcome_metadata={
            "message": execution_result.get(
                "message"
            )
        },
        completed_at=datetime.now(
            timezone.utc
        )
    )

    db.add(outcome)

    # ========================================================
    # SUCCESSFUL RECOVERY
    # ========================================================

    if (
        status == "SUCCESS"
        and recovered_amount > 0
    ):

        case.recovered = True

        case.recovered_at = datetime.now(
            timezone.utc
        )

        case.recovery_status = "RECOVERED"

        case.execution_status = "RECOVERED"

    # ========================================================
    # FAILED RECOVERY
    # ========================================================

    else:

        case.recovery_status = "NOT_RECOVERED"

        case.execution_status = "FAILED"

    db.flush()

    return {
        "case_id": case.case_id,
        "outcome_id": outcome.id,
        "status": status,
        "recovered": case.recovered,
        "recovery_status": case.recovery_status,
        "recovered_amount": recovered_amount
    }