from typing import Optional

from app.models import CheckoutSession


def detect_checkout_abandonment(
    session: CheckoutSession
) -> Optional[dict]:
    """
    Detect checkout sessions that were abandoned
    before payment completion.

    Returns a normalized detection object,
    or None if the checkout was completed.
    """

    status = (session.status or "").upper()

    if status != "CHECKOUT_ABANDONED":
        return None

    metadata = session.session_metadata or {}

    return {
        "case_type": "CHECKOUT_ABANDONMENT",

        "session_id": session.session_id,

        "merchant_id": session.merchant_id,

        "customer_id": session.customer_id,

        "amount": session.amount,

        "failure_reason": "CHECKOUT_ABANDONED",

        "abandonment_reason": metadata.get(
            "abandonment_reason"
        ),

        "device": metadata.get(
            "device"
        ),

        "browser": metadata.get(
            "browser"
        ),

        "created_at": session.started_at,
    }