from app.classification.rules import (
    classify_with_rules
)


RULE_CONFIDENCE_THRESHOLD = 0.80


def classify_failure(
    failure_reason: str
) -> dict:
    """
    Classify a revenue-risk event.

    Clear cases are handled by deterministic rules.
    Ambiguous cases are routed to the AI layer.
    """

    result = classify_with_rules(
        failure_reason
    )

    # -------------------------------
    # Clear deterministic case
    # -------------------------------

    if (
        result["confidence"]
        >= RULE_CONFIDENCE_THRESHOLD
    ):

        return result

    # -------------------------------
    # Ambiguous case
    # -------------------------------

    return classify_ambiguous_with_ai(
        failure_reason
    )


def classify_ambiguous_with_ai(
    failure_reason: str
) -> dict:
    """
    AI classification boundary.

    Phase 2 uses a deterministic fallback so the
    system remains fully runnable without an
    external LLM API.

    This function will become the real AI
    classifier in a later phase.
    """

    reason = (
        failure_reason or ""
    ).upper()

    # Infrastructure signals

    if any(
        keyword in reason
        for keyword in [
            "TIMEOUT",
            "GATEWAY",
            "NETWORK",
            "SERVER",
            "BANK"
        ]
    ):

        return {
            "classification":
                "SYSTEM_FAILURE",

            "confidence": 0.82,

            "reason":
                "AI fallback detected infrastructure-related "
                "failure characteristics.",

            "routing": "AI"
        }

    # Recoverable customer/payment signals

    if any(
        keyword in reason
        for keyword in [
            "RETRY",
            "OTP",
            "AUTH",
            "TEMPORARY"
        ]
    ):

        return {
            "classification":
                "SOFT_FAILURE",

            "confidence": 0.78,

            "reason":
                "AI fallback detected potentially recoverable "
                "payment characteristics.",

            "routing": "AI"
        }

    # Still uncertain

    return {
        "classification":
            "AMBIGUOUS",

        "confidence": 0.50,

        "reason":
            "AI could not confidently determine "
            "the failure category.",

        "routing": "AI"
    }