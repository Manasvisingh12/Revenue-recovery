from typing import Optional

from app.models import PaymentEvent


PAYMENT_FAILURE_STATUSES = {
    "INSUFFICIENT_FUNDS",
    "GATEWAY_TIMEOUT",
    "BANK_TIMEOUT",
    "CARD_EXPIRED",
    "UNKNOWN_ERROR",
    "TEMPORARY_AUTH_ERROR",
}


def detect_payment_failure(
    event: PaymentEvent
) -> Optional[dict]:
    """
    Detect whether a payment event represents
    a revenue-risk event.

    Known and ambiguous payment failures are both
    detected here and passed to the classification
    layer.

    Returns a normalized detection object,
    or None if the event is not a payment failure.
    """

    status = (
        event.status or ""
    ).upper().strip()

    if status not in PAYMENT_FAILURE_STATUSES:
        return None

    payload = event.payload or {}

    return {
        "case_type": "PAYMENT_FAILURE",

        "event_id": event.event_id,

        "merchant_id": event.merchant_id,

        "customer_id": payload.get(
            "customer_id"
        ),

        "payment_id": event.payment_id,

        "amount": event.amount or 0,

        "failure_reason": status,

        "gateway": payload.get(
            "gateway"
        ),

        "bank": payload.get(
            "bank"
        ),

        "failure_category": payload.get(
            "failure_category"
        ),

        "incident": payload.get(
            "incident"
        ),

        "created_at": event.created_at,
    }