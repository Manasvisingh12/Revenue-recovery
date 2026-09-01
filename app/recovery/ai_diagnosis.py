def diagnose_case(
    case
) -> dict:
    """
    Recovery intelligence diagnosis.

    This is currently an explainable deterministic
    AI boundary.

    A real LLM can replace this implementation
    later without changing the recovery pipeline.
    """

    reason = (
        case.failure_reason
        or ""
    ).upper()

    # ---------------------------------
    # INFRASTRUCTURE INCIDENT
    # ---------------------------------

    if case.incident_detected:

        return {
            "diagnosis":
                "Payment recovery opportunity is likely "
                "associated with a detected infrastructure "
                "incident.",

            "confidence":
                0.92,

            "suggested_action":
                "WAIT",

            "reason":
                "A provider or infrastructure incident "
                "was detected for this case."
        }

    # ---------------------------------
    # SOFT FAILURE
    # ---------------------------------

    if case.classification == "SOFT_FAILURE":

        return {
            "diagnosis":
                "Payment failure appears temporary and "
                "has strong recovery potential.",

            "confidence":
                0.88,

            "suggested_action":
                "RETRY",

            "reason":
                "Soft failures are generally recoverable "
                "through controlled retry."
        }

    # ---------------------------------
    # HARD FAILURE
    # ---------------------------------

    if case.classification == "HARD_FAILURE":

        if (
            "CARD_EXPIRED"
            in reason
        ):

            return {
                "diagnosis":
                    "Customer payment method requires "
                    "an update before recovery.",

                "confidence":
                    0.95,

                "suggested_action":
                    "MESSAGE",

                "reason":
                    "An expired card requires customer action."
            }

        if (
            "INSUFFICIENT_FUNDS"
            in reason
        ):

            return {
                "diagnosis":
                    "Payment may succeed if the customer "
                    "uses another payment method.",

                "confidence":
                    0.90,

                "suggested_action":
                    "MESSAGE",

                "reason":
                    "Insufficient funds require customer action."
            }

        return {
            "diagnosis":
                "Failure appears difficult to recover "
                "automatically.",

            "confidence":
                0.90,

            "suggested_action":
                "STOP",

            "reason":
                "Hard failure indicates low automated "
                "recovery potential."
        }

    # ---------------------------------
    # CHECKOUT ABANDONMENT
    # ---------------------------------

    if (
        case.case_type
        == "CHECKOUT_ABANDONMENT"
    ):

        return {
            "diagnosis":
                "Customer abandoned checkout before "
                "payment completion.",

            "confidence":
                0.82,

            "suggested_action":
                "MESSAGE",

            "reason":
                "Customer re-engagement may recover "
                "the abandoned revenue."
        }

    # ---------------------------------
    # AMBIGUOUS
    # ---------------------------------

    return {
        "diagnosis":
            "The recovery opportunity does not have "
            "enough evidence for a high-confidence "
            "automated action.",

        "confidence":
            0.45,

        "suggested_action":
            "ESCALATE",

        "reason":
            "Low confidence requires additional review."
    }