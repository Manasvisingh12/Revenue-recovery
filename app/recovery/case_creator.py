import uuid

from sqlalchemy.orm import Session

from app.models import RecoveryCase
from app.classification.classifier import classify_failure


def generate_case_id() -> str:
    return f"case_{uuid.uuid4().hex[:12]}"


def create_recovery_case(
    db: Session,
    detection: dict
) -> RecoveryCase:
    """
    Convert a detected revenue-risk event
    into a persistent RecoveryCase.
    """

    classification = classify_failure(
        detection["failure_reason"]
    )

    amount = detection.get("amount") or 0

    case = RecoveryCase(
        case_id=generate_case_id(),

        merchant_id=detection["merchant_id"],

        customer_id=detection.get("customer_id"),

        payment_id=detection.get("payment_id"),

        checkout_id=detection.get("session_id"),

        case_type=detection["case_type"],

        amount=amount,

        currency="INR",

        revenue_at_risk=amount,

        failure_reason=detection[
            "failure_reason"
        ],

        classification=classification[
            "classification"
        ],

        confidence=classification[
            "confidence"
        ],

        classification_reason=classification[
            "reason"
        ],

        routing=classification[
            "routing"
        ],

        recommended_action=
            recommend_action(
                classification["classification"],
                detection["failure_reason"]
            ),

        status="OPEN"
    )

    db.add(case)

    return case


def recommend_action(
    classification: str,
    failure_reason: str
) -> str:

    if classification == "HARD_FAILURE":

        if failure_reason == "INSUFFICIENT_FUNDS":
            return "REQUEST_ALTERNATIVE_PAYMENT_METHOD"

        if failure_reason == "CARD_EXPIRED":
            return "REQUEST_CARD_UPDATE"

        return "CUSTOMER_REVIEW"

    if classification == "SOFT_FAILURE":

        return "RETRY_CHECKOUT"

    if classification == "SYSTEM_FAILURE":

        return "RETRY_WITH_ALTERNATE_ROUTE"

    return "AI_REVIEW"