from sqlalchemy.orm import Session

from app.models import RecoveryCase, RecoveryPostmortem
from app.recovery.audit_trail import get_case_timeline


def save_recovery_postmortem(
    db: Session,
    case: RecoveryCase,
    postmortem: dict,
):
    failure = postmortem.get("failure", {})
    ai = postmortem.get("ai_decision", {})
    recovery = postmortem.get("recovery", {})

    existing = (
        db.query(RecoveryPostmortem)
        .filter(
            RecoveryPostmortem.case_id == case.case_id
        )
        .first()
    )

    if existing:
        return existing

    timeline = get_case_timeline(
        db,
        case.case_id,
    )

    timeline_data = [
        {
            "event_type": event.event_type,
            "source": event.event_source,
            "decision": event.decision,
            "reasoning": event.reasoning,
            "guardrail_result": event.guardrail_result,
            "execution_result": event.execution_result,
            "metadata": event.audit_metadata,
        }
        for event in timeline
    ]

    record = RecoveryPostmortem(
        case_id=case.case_id,
        merchant_id=case.merchant_id,
        failure_stage=postmortem.get(
            "failure_stage",
            "RECOVERY_EXECUTION",
        ),
        attempted_action=ai.get(
            "decision",
            case.recommended_action,
        ),
        failure_reason=failure.get(
            "reason",
            "UNKNOWN",
        ),
        root_cause=postmortem.get(
            "root_cause",
            failure.get(
                "reason",
                "UNKNOWN",
            ),
        ),
        ai_diagnosis=ai.get(
            "reasoning",
            case.ai_diagnosis,
        ),
        guardrail_result=postmortem.get(
            "guardrail"
        ),
        execution_result=postmortem.get(
            "execution"
        ),
        recovery_status=postmortem.get(
            "final_state",
            case.recovery_status,
        ),
        recovered_amount=recovery.get(
            "recovered_amount",
            0,
        ),
        recommended_followup=postmortem.get(
            "recommended_follow_up",
            "Review recovery strategy and investigate failure.",
        ),
        postmortem_metadata={
            "timeline": timeline_data,
            "ai_decision": ai,
            "recovery": recovery,
        },
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def generate_recovery_postmortem(
    db: Session,
    case: RecoveryCase,
):
    if case.recovered:
        return None

    if case.recovery_status == "RECOVERED":
        return None

    recovered_amount = 0

    postmortem = {
        "failure_stage": "RECOVERY_EXECUTION",
        "failure": {
            "reason": case.execution_status,
        },
        "ai_decision": {
            "decision": case.recommended_action,
            "reasoning": case.ai_diagnosis,
        },
        "guardrail": {
            "execution_status": case.execution_status,
        },
        "execution": {
            "recovered": False,
            "recovered_amount": recovered_amount,
        },
        "final_state": case.recovery_status,
        "recovery": {
            "recovered_amount": recovered_amount,
        },
        "recommended_follow_up": (
            "Review recovery strategy and investigate failure."
        ),
    }

    return save_recovery_postmortem(
        db,
        case,
        postmortem,
    )
