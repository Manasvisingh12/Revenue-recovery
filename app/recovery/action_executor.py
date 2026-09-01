import time

from sqlalchemy.orm import Session

from app.models import (
    RecoveryCase,
    RecoveryActionLog,
)

from app.recovery.guardrails.guardrail_engine import (
    validate_recovery_action,
)

from app.recovery.audit_trail import (
    record_audit_event,
)

from app.recovery.recovery_metrics import (
    recovery_latency,
)

from app.recovery.outcome_tracker import (
    track_recovery_outcome,
)

from app.recovery.message_executor import (
    execute_recovery_message,
)


def execute_recovery_action(
    db: Session,
    case: RecoveryCase,
) -> dict:

    start_time = time.perf_counter()

    try:

        requested_action = (
            case.recommended_action
            or "NO_ACTION"
        )

        action_map = {
            "RETRY_CHECKOUT": "RETRY",
            "RETRY_WITH_ALTERNATE_ROUTE": "RETRY",
            "REQUEST_ALTERNATIVE_PAYMENT_METHOD": "MESSAGE",
            "REQUEST_CARD_UPDATE": "MESSAGE",
            "CUSTOMER_REVIEW": "ESCALATE",
            "AI_REVIEW": "ESCALATE",
            "RETRY": "RETRY",
            "WAIT": "WAIT",
            "MESSAGE": "MESSAGE",
            "ESCALATE": "ESCALATE",
            "NO_ACTION": "NO_ACTION",
            "STOP": "STOP",
        }

        action = action_map.get(
            requested_action,
            "STOP",
        )

        record_audit_event(
            db,
            case,
            event_type="AI_DECISION",
            event_source="RECOVERY_INTELLIGENCE",
            decision=action,
            reasoning=case.ai_diagnosis,
            metadata={
                "requested_action": requested_action,
                "normalized_action": action,
            },
        )

        # ====================================================
        # GUARDRAIL VALIDATION
        # ====================================================

        validation = validate_recovery_action(
            db,
            case,
            action,
        )

        final_action = validation.get(
            "action",
            action,
        )

        reason = validation.get(
            "reason",
            "UNKNOWN",
        )

        allowed = validation.get(
            "allowed",
            False,
        )

        record_audit_event(
            db,
            case,
            event_type="GUARDRAIL_EVALUATION",
            event_source="GUARDRAIL_ENGINE",
            decision=final_action,
            reasoning=reason,
            guardrail_result=validation,
            metadata={
                "requested_action": action,
                "final_action": final_action,
                "allowed": allowed,
            },
        )

        # ====================================================
        # BLOCKED BY GUARDRAILS
        # ====================================================

        if not allowed:

            log = RecoveryActionLog(
                case_id=case.case_id,
                merchant_id=case.merchant_id,
                customer_id=case.customer_id,
                action=final_action,
                status="BLOCKED",
                block_reason=reason,
                estimated_cost=0,
            )

            db.add(log)

            case.execution_status = "BLOCKED"

            execution_result = {
                "executed": False,
                "blocked": True,
                "escalated": False,
                "action": final_action,
                "reason": reason,
                "status": "BLOCKED",
                "recovered_amount": 0,
            }

            record_audit_event(
                db,
                case,
                event_type="RECOVERY_EXECUTION",
                event_source="ACTION_EXECUTOR",
                decision=final_action,
                reasoning=reason,
                guardrail_result=validation,
                execution_result=execution_result,
            )

            return execution_result

        # ====================================================
        # ESCALATE
        # ====================================================

        if final_action == "ESCALATE":

            log = RecoveryActionLog(
                case_id=case.case_id,
                merchant_id=case.merchant_id,
                customer_id=case.customer_id,
                action="ESCALATE",
                status="ESCALATED",
                block_reason=reason,
                estimated_cost=0,
            )

            db.add(log)

            case.execution_status = "ESCALATED"

            execution_result = {
                "executed": False,
                "blocked": False,
                "escalated": True,
                "action": "ESCALATE",
                "reason": reason,
                "status": "ESCALATED",
                "recovered_amount": 0,
            }

            record_audit_event(
                db,
                case,
                event_type="RECOVERY_EXECUTION",
                event_source="ACTION_EXECUTOR",
                decision="ESCALATE",
                reasoning=reason,
                guardrail_result=validation,
                execution_result=execution_result,
            )

            return execution_result

        # ====================================================
        # NO ACTION
        # ====================================================

        if final_action == "NO_ACTION":

            log = RecoveryActionLog(
                case_id=case.case_id,
                merchant_id=case.merchant_id,
                customer_id=case.customer_id,
                action="NO_ACTION",
                status="SKIPPED",
                block_reason=reason,
                estimated_cost=0,
            )

            db.add(log)

            case.execution_status = "SKIPPED"

            execution_result = {
                "executed": False,
                "blocked": False,
                "escalated": False,
                "action": "NO_ACTION",
                "reason": reason,
                "status": "SKIPPED",
                "recovered_amount": 0,
            }

            record_audit_event(
                db,
                case,
                event_type="RECOVERY_EXECUTION",
                event_source="ACTION_EXECUTOR",
                decision="NO_ACTION",
                reasoning=reason,
                guardrail_result=validation,
                execution_result=execution_result,
            )

            return execution_result

        # ====================================================
        # STOP
        # ====================================================

        if final_action == "STOP":

            log = RecoveryActionLog(
                case_id=case.case_id,
                merchant_id=case.merchant_id,
                customer_id=case.customer_id,
                action="STOP",
                status="BLOCKED",
                block_reason=reason,
                estimated_cost=0,
            )

            db.add(log)

            case.execution_status = "BLOCKED"

            execution_result = {
                "executed": False,
                "blocked": True,
                "escalated": False,
                "action": "STOP",
                "reason": reason,
                "status": "BLOCKED",
                "recovered_amount": 0,
            }

            record_audit_event(
                db,
                case,
                event_type="RECOVERY_EXECUTION",
                event_source="ACTION_EXECUTOR",
                decision="STOP",
                reasoning=reason,
                guardrail_result=validation,
                execution_result=execution_result,
            )

            return execution_result

        # ====================================================
        # MESSAGE RECOVERY
        # ====================================================

        if final_action == "MESSAGE":

            message_result = execute_recovery_message(
                db,
                case,
            )

            log = RecoveryActionLog(
                case_id=case.case_id,
                merchant_id=case.merchant_id,
                customer_id=case.customer_id,
                action="MESSAGE",
                status="EXECUTED",
                block_reason=None,
                estimated_cost=0,
            )

            db.add(log)

            case.execution_status = "EXECUTED"

            execution_result = {
                "executed": True,
                "blocked": False,
                "escalated": False,
                "action": "MESSAGE",
                "reason": reason,
                "status": "SENT",
                "recovered_amount": 0,
                "payment_link": message_result.get(
                    "payment_link"
                ),
                "message": message_result.get(
                    "message"
                ),
                "message_status": "SENT",
            }

            record_audit_event(
                db,
                case,
                event_type="RECOVERY_EXECUTION",
                event_source="ACTION_EXECUTOR",
                decision="MESSAGE",
                reasoning=reason,
                guardrail_result=validation,
                execution_result=execution_result,
            )

            return execution_result

        # ====================================================
        # RETRY RECOVERY
        # ====================================================

        if final_action == "RETRY":

            case.retry_count += 1

            log = RecoveryActionLog(
                case_id=case.case_id,
                merchant_id=case.merchant_id,
                customer_id=case.customer_id,
                action="RETRY",
                status="EXECUTED",
                block_reason=None,
                estimated_cost=0,
            )

            db.add(log)

            # ------------------------------------------------
            # Simulated successful payment recovery.
            #
            # This is a hackathon simulation, so an allowed
            # retry represents the payment succeeding.
            # ------------------------------------------------

            execution_result = {
                "executed": True,
                "blocked": False,
                "escalated": False,
                "action": "RETRY",
                "reason": reason,
                "status": "SUCCESS",
                "recovered_amount": case.amount,
            }

            outcome_result = track_recovery_outcome(
                db,
                case,
                execution_result,
            )

            record_audit_event(
                db,
                case,
                event_type="RECOVERY_EXECUTION",
                event_source="ACTION_EXECUTOR",
                decision="RETRY",
                reasoning=reason,
                guardrail_result=validation,
                execution_result={
                    **execution_result,
                    "outcome": outcome_result,
                },
            )

            return {
                **execution_result,
                "outcome_id": outcome_result.get(
                    "outcome_id"
                ),
                "recovery_status": outcome_result.get(
                    "recovery_status"
                ),
            }

        # ====================================================
        # UNSUPPORTED ACTION
        # ====================================================

        case.execution_status = "BLOCKED"

        execution_result = {
            "executed": False,
            "blocked": True,
            "escalated": False,
            "action": final_action,
            "reason": "UNSUPPORTED_ACTION",
            "status": "FAILED",
            "recovered_amount": 0,
        }

        record_audit_event(
            db,
            case,
            event_type="RECOVERY_EXECUTION",
            event_source="ACTION_EXECUTOR",
            decision=final_action,
            reasoning="Unsupported recovery action.",
            guardrail_result=validation,
            execution_result=execution_result,
        )

        return execution_result

    finally:

        elapsed = time.perf_counter() - start_time

        recovery_latency.observe(elapsed)