from sqlalchemy.orm import Session

from app.models import (
    PaymentEvent,
    CheckoutSession,
    RecoveryCase,
)

from app.detection.payment_failure_detector import (
    detect_payment_failure,
)

from app.detection.abandonment_detector import (
    detect_checkout_abandonment,
)

from app.detection.incident_detector import (
    detect_incidents,
)

from app.recovery.case_creator import (
    create_recovery_case,
)

from app.recovery.recovery_engine import (
    process_recovery_intelligence,
)

from app.recovery.guardrails_processor import (
    process_recovery_actions,
)

from app.recovery.audit_trail import (
    record_audit_event,
)


def process_payment_events(db: Session) -> int:

    events = db.query(PaymentEvent).all()

    created = 0

    for event in events:

        detection = detect_payment_failure(event)

        if detection is None:
            continue

        existing = (
            db.query(RecoveryCase)
            .filter(
                RecoveryCase.payment_id == event.payment_id,
                RecoveryCase.case_type == "PAYMENT_FAILURE"
            )
            .first()
        )

        if existing:
            continue

        case = create_recovery_case(
            db,
            detection
        )

        record_audit_event(
            db=db,
            case=case,
            event_type="CASE_CREATED",
            event_source="FAILURE_DETECTOR",
            decision=None,
            reasoning=case.failure_reason,
            metadata={
                "case_type": case.case_type,
                "amount": case.amount,
                "failure_reason": case.failure_reason,
            }
        )

        created += 1

    return created


def process_checkout_sessions(db: Session) -> int:

    sessions = db.query(CheckoutSession).all()

    created = 0

    for session in sessions:

        detection = detect_checkout_abandonment(session)

        if detection is None:
            continue

        existing = (
            db.query(RecoveryCase)
            .filter(
                RecoveryCase.checkout_id == session.session_id,
                RecoveryCase.case_type == "CHECKOUT_ABANDONMENT"
            )
            .first()
        )

        if existing:
            continue

        case = create_recovery_case(
            db,
            detection
        )

        record_audit_event(
            db=db,
            case=case,
            event_type="CASE_CREATED",
            event_source="ABANDONMENT_DETECTOR",
            decision=None,
            reasoning="Checkout abandonment detected.",
            metadata={
                "case_type": case.case_type,
                "amount": case.amount,
            }
        )

        created += 1

    return created


def enrich_cases_with_incidents(db: Session) -> dict:

    events = db.query(PaymentEvent).all()

    incident_result = detect_incidents(events)

    all_incidents = (
        incident_result["gateway_incidents"]
        +
        incident_result["bank_incidents"]
    )

    enriched = 0

    for incident in all_incidents:

        payment_ids = incident["payment_ids"]

        cases = (
            db.query(RecoveryCase)
            .filter(
                RecoveryCase.payment_id.in_(payment_ids)
            )
            .all()
        )

        for case in cases:

            case.incident_detected = True

            case.incident_type = incident[
                "incident_type"
            ]

            case.incident_provider = incident[
                "provider"
            ]

            record_audit_event(
                db=db,
                case=case,
                event_type="INCIDENT_DETECTED",
                event_source="INCIDENT_DETECTOR",
                decision="WAIT",
                reasoning=(
                    "Infrastructure incident detected. "
                    "Recovery action should account for provider instability."
                ),
                metadata={
                    "incident_type": incident[
                        "incident_type"
                    ],
                    "provider": incident[
                        "provider"
                    ],
                }
            )

            enriched += 1

    return {
        "incidents_detected": len(all_incidents),
        "cases_enriched": enriched,
        "incident_revenue_at_risk": sum(
            incident["revenue_at_risk"]
            for incident in all_incidents
        )
    }


def process_batch(db: Session) -> dict:

    payment_cases = process_payment_events(db)

    checkout_cases = process_checkout_sessions(db)

    incident_result = enrich_cases_with_incidents(db)

    db.commit()

    intelligence_result = process_recovery_intelligence(db)

    db.commit()

    guardrail_result = process_recovery_actions(db)

    db.commit()

    return {
        "payment_cases_created": payment_cases,
        "checkout_cases_created": checkout_cases,
        "total_cases_created": (
            payment_cases + checkout_cases
        ),
        "incidents_detected": incident_result[
            "incidents_detected"
        ],
        "cases_enriched": incident_result[
            "cases_enriched"
        ],
        "incident_revenue_at_risk": incident_result[
            "incident_revenue_at_risk"
        ],
        "recovery_cases_analyzed": intelligence_result[
            "cases_analyzed"
        ],
        "actions_evaluated": guardrail_result[
            "actions_evaluated"
        ],
        "actions_allowed": guardrail_result[
            "actions_allowed"
        ],
        "actions_blocked": guardrail_result[
            "actions_blocked"
        ],
        "actions_escalated": guardrail_result[
            "actions_escalated"
        ],
        "guardrail_reasons": guardrail_result[
            "guardrail_reasons"
        ],
    }
