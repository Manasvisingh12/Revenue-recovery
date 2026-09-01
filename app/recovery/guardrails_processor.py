
from sqlalchemy.orm import Session

from app.models import RecoveryCase

from app.recovery.action_executor import execute_recovery_action

from app.recovery.audit_trail import record_audit_event

from app.recovery.recovery_metrics import (
    guardrail_blocks_total,
    ai_decisions_total
)


def process_recovery_actions(
    db: Session
) -> dict:

    cases = (
        db.query(RecoveryCase)
        .filter(
            RecoveryCase.execution_status == 'PENDING'
        )
        .all()
    )

    actions_evaluated = 0
    actions_allowed = 0
    actions_blocked = 0
    actions_escalated = 0

    guardrail_reasons = {}

    for case in cases:

        action = (
            case.recommended_action
            or 'NO_ACTION'
        )

        actions_evaluated += 1

        # ====================================================
        # PROMETHEUS — AI DECISION
        # ====================================================

        ai_decisions_total.labels(
            action=action
        ).inc()

        # ====================================================
        # RECORD AI DECISION
        # ====================================================

        record_audit_event(
            db=db,
            case=case,
            event_type='AI_DECISION',
            event_source='RECOVERY_INTELLIGENCE',
            decision=action,
            reasoning=(
                case.action_reason
                or case.ai_diagnosis
            ),
            metadata={
                'ai_confidence':
                    case.ai_confidence,

                'opportunity_score':
                    case.opportunity_score,

                'recovery_probability':
                    case.recovery_probability,

                'expected_recovery_value':
                    case.expected_recovery_value
            }
        )

        # ====================================================
        # EXECUTE RECOVERY ACTION
        # ====================================================

        result = execute_recovery_action(
            db,
            case
        )

        # ====================================================
        # PROMETHEUS — GUARDRAIL BLOCKS
        # ====================================================

        if result.get('allowed') is True:

            actions_allowed += 1

        else:

            actions_blocked += 1

            guardrail_blocks_total.labels(
                reason=result.get(
                    'reason',
                    'UNKNOWN'
                )
            ).inc()

        # ====================================================
        # ESCALATIONS
        # ====================================================

        if result.get('action') == 'ESCALATE':

            actions_escalated += 1

        # ====================================================
        # GUARDRAIL REASON SUMMARY
        # ====================================================

        reason = result.get(
            'reason',
            'UNKNOWN'
        )

        guardrail_reasons[reason] = (
            guardrail_reasons.get(reason, 0) + 1
        )

    return {
        'actions_evaluated':
            actions_evaluated,

        'actions_allowed':
            actions_allowed,

        'actions_blocked':
            actions_blocked,

        'actions_escalated':
            actions_escalated,

        'guardrail_reasons':
            guardrail_reasons
    }

