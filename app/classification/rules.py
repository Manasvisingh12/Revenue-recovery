from app.classification.failure_types import (
    FailureClassification
)


HARD_FAILURE_REASONS = {
    "INSUFFICIENT_FUNDS",
    "CARD_EXPIRED",
}


SYSTEM_FAILURE_REASONS = {
    "GATEWAY_TIMEOUT",
    "BANK_TIMEOUT",
}


SOFT_FAILURE_REASONS = {
    "CHECKOUT_ABANDONED",
}


def classify_with_rules(
    failure_reason: str
) -> dict:
    """
    Deterministic classification for known
    payment and checkout failure reasons.
    """

    reason = (
        failure_reason or ""
    ).upper().strip()

    # -------------------------------
    # Permanent customer failures
    # -------------------------------

    if reason in HARD_FAILURE_REASONS:

        return {
            "classification":
                FailureClassification.HARD_FAILURE.value,

            "confidence": 0.98,

            "reason":
                f"Known permanent customer-side failure: {reason}",

            "routing": "RULES"
        }

    # -------------------------------
    # Infrastructure failures
    # -------------------------------

    if reason in SYSTEM_FAILURE_REASONS:

        return {
            "classification":
                FailureClassification.SYSTEM_FAILURE.value,

            "confidence": 0.98,

            "reason":
                f"Known infrastructure failure: {reason}",

            "routing": "RULES"
        }

    # -------------------------------
    # Recoverable failures
    # -------------------------------

    if reason in SOFT_FAILURE_REASONS:

        return {
            "classification":
                FailureClassification.SOFT_FAILURE.value,

            "confidence": 0.96,

            "reason":
                f"Potentially recoverable revenue event: {reason}",

            "routing": "RULES"
        }

    # -------------------------------
    # Unknown case
    # -------------------------------

    return {
        "classification":
            FailureClassification.AMBIGUOUS.value,

        "confidence": 0.40,

        "reason":
            f"No deterministic rule matched: {reason}",

        "routing": "AI"
    }