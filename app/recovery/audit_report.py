from sqlalchemy.orm import Session

from app.models import RecoveryCase
from app.recovery.audit_trail import (
    get_case_timeline
)


def generate_audit_report(
    db: Session,
    case_id: str
):

    case = (
        db.query(RecoveryCase)
        .filter(
            RecoveryCase.case_id
            == case_id
        )
        .first()
    )

    if not case:
        return None

    events = get_case_timeline(
        db,
        case_id
    )

    return {
        "case": {
            "case_id": case.case_id,
            "case_type": case.case_type,
            "failure_reason":
                case.failure_reason,
            "amount": case.amount,
            "revenue_at_risk":
                case.revenue_at_risk,
            "recovery_status":
                case.recovery_status,
        },

        "ai": {
            "recommended_action":
                case.recommended_action,
            "diagnosis":
                case.ai_diagnosis,
            "confidence":
                case.ai_confidence,
            "reason":
                case.action_reason,
        },

        "timeline": [
            {
                "timestamp":
                    event.created_at,

                "event":
                    event.event_type,

                "source":
                    event.event_source,

                "decision":
                    event.decision,

                "reasoning":
                    event.reasoning,

                "guardrails":
                    event.guardrail_result,

                "execution":
                    event.execution_result,
            }

            for event in events
        ]
    }