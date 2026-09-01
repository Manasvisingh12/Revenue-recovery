from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import RecoveryCase, RecoveryOutcome

from app.recovery.payment_link import (
    generate_recovery_payment_link
)

from app.recovery.checkout_message import (
    generate_checkout_message
)


def execute_recovery_message(
    db: Session,
    case: RecoveryCase
) -> dict:

    payment_link = generate_recovery_payment_link(case)

    message = generate_checkout_message(
        case,
        payment_link
    )

    outcome = RecoveryOutcome(
        case_id=case.case_id,
        merchant_id=case.merchant_id,
        payment_id=case.payment_id,
        checkout_id=case.checkout_id,
        action="MESSAGE",
        status="SENT",
        amount=case.amount,
        recovered_amount=0,
        payment_link=payment_link,
        message_status="SENT",
        outcome_metadata={
            "message": message
        }
    )

    db.add(outcome)

    return {
        "case_id": case.case_id,
        "action": "MESSAGE",
        "status": "SENT",
        "payment_link": payment_link,
        "message": message
    }