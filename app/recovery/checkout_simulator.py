from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import RecoveryCase, RecoveryOutcome


def simulate_checkout_completion(
    db: Session,
    case: RecoveryCase
) -> dict:

    outcome = (
        db.query(RecoveryOutcome)
        .filter(
            RecoveryOutcome.case_id == case.case_id,
            RecoveryOutcome.action == "MESSAGE",
            RecoveryOutcome.status == "SENT"
        )
        .order_by(
            RecoveryOutcome.id.desc()
        )
        .first()
    )

    if outcome is None:
        return {
            "success": False,
            "reason": "NO_ACTIVE_RECOVERY_LINK"
        }

    outcome.status = "SUCCESS"
    outcome.recovered_amount = case.amount
    outcome.message_status = "CONVERTED"
    outcome.completed_at = datetime.now(timezone.utc)

    case.recovered = True
    case.recovery_status = "RECOVERED"
    case.recovered_at = datetime.now(timezone.utc)
    case.execution_status = "EXECUTED"

    db.commit()

    return {
        "success": True,
        "case_id": case.case_id,
        "status": "SUCCESS",
        "recovered_amount": case.amount,
        "recovery_status": case.recovery_status
    }