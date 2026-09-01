from app.recovery.recovery_metrics import ai_decisions_total
def determine_priority(
    expected_recovery_value: float,
    opportunity_score: float
) -> str:

    if (
        expected_recovery_value >= 10000
        and opportunity_score >= 70
    ):

        return "CRITICAL"

    if (
        expected_recovery_value >= 5000
        or opportunity_score >= 80
    ):

        return "HIGH"

    if (
        expected_recovery_value >= 1000
        or opportunity_score >= 50
    ):

        return "MEDIUM"

    return "LOW"


def recommend_recovery_action(
    case,
    opportunity_score: float,
    recovery_probability: float,
    expected_recovery_value: float,
    ai_diagnosis: dict
) -> dict:
    """
    Make the final recovery decision.

    Rules provide safety and consistency.
    AI diagnosis provides additional intelligence.
    """

    ai_confidence = (
        ai_diagnosis["confidence"]
    )

    priority = determine_priority(
        expected_recovery_value,
        opportunity_score
    )

    action = None
    reason = None

    # ---------------------------------
    # 1. STOP
    # ---------------------------------

    if (
        case.classification
        == "HARD_FAILURE"
        and ai_diagnosis[
            "suggested_action"
        ]
        == "STOP"
    ):

        action = "STOP"

        priority = "LOW"

        reason = ai_diagnosis[
            "reason"
        ]

    # ---------------------------------
    # 2. ESCALATE
    # ---------------------------------

    elif (
        case.classification
        == "AMBIGUOUS"
        and (
            ai_confidence < 0.60
            or expected_recovery_value >= 10000
        )
    ):

        action = "ESCALATE"

        reason = (
            "High-value or low-confidence ambiguous "
            "case requires human review."
        )

    # ---------------------------------
    # 3. NO ACTION
    # ---------------------------------

    elif (
        expected_recovery_value < 100
        and opportunity_score < 30
    ):

        action = "NO_ACTION"

        priority = "LOW"

        reason = (
            "Expected recovery value is too low to "
            "justify recovery effort."
        )

    # ---------------------------------
    # 4. WAIT
    # ---------------------------------

    elif case.incident_detected:

        action = "WAIT"

        reason = (
            "Infrastructure incident detected. "
            "Wait for the provider to stabilize "
            "before retrying."
        )

    # ---------------------------------
    # 5. MESSAGE
    # ---------------------------------

    elif (
        case.case_type
        == "CHECKOUT_ABANDONMENT"
    ):

        action = "MESSAGE"

        reason = (
            "Customer abandoned checkout and should "
            "be re-engaged."
        )

    elif (
        ai_diagnosis[
            "suggested_action"
        ]
        == "MESSAGE"
    ):

        action = "MESSAGE"

        reason = ai_diagnosis[
            "reason"
        ]

    # ---------------------------------
    # 6. RETRY
    # ---------------------------------

    elif (
        case.classification
        == "SOFT_FAILURE"
        and recovery_probability >= 0.50
    ):

        action = "RETRY"

        reason = (
            "Temporary failure has sufficient "
            "recovery probability for retry."
        )

    # ---------------------------------
    # DEFAULT
    # ---------------------------------

    else:

        action = "NO_ACTION"

        reason = (
            "No economically justified automated "
            "recovery action was identified."
        )

    # ---------------------------------
    # PROMETHEUS
    # ---------------------------------

    ai_decisions_total.labels(
        action=action
    ).inc()

    return {
        "action": action,
        "priority": priority,
        "reason": reason
    }