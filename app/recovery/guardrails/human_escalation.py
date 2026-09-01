def requires_human_escalation(
    case
) -> dict:

    # Phase 3 explicitly decided escalation

    if (
        case.recommended_action
        == "ESCALATE"
    ):

        return {
            "required": True,

            "reason":
                "Phase 3 recommended human escalation."
        }

    # Low AI confidence
    if (
        case.ai_confidence is not None
        and case.ai_confidence < 0.60
    ):

        return {
            "required": True,

            "reason":
                "AI confidence is below the safe automation threshold."
        }

    # High value ambiguous case
    if (
        case.classification
        == "AMBIGUOUS"
        and (
            case.expected_recovery_value
            or 0
        )
        >= 10000
    ):

        return {
            "required": True,

            "reason":
                "High-value ambiguous case requires human review."
        }

    return {
        "required": False,

        "reason":
            "Automated action is eligible for evaluation."
    }