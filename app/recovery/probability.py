def calculate_recovery_probability(
    case
) -> dict:
    """
    Estimate the probability that the revenue
    can be recovered.
    """

    probability = 0.0

    reasons = []

    classification = (
        case.classification
    )

    # ---------------------------------
    # BASE PROBABILITY
    # ---------------------------------

    if classification == "SOFT_FAILURE":

        probability = 0.75

        reasons.append(
            "Soft failures have strong recovery potential."
        )

    elif classification == "SYSTEM_FAILURE":

        probability = 0.65

        reasons.append(
            "System failures may recover after infrastructure stabilizes."
        )

    elif classification == "AMBIGUOUS":

        probability = 0.40

        reasons.append(
            "Ambiguous failures have uncertain recovery potential."
        )

    elif classification == "HARD_FAILURE":

        probability = 0.10

        reasons.append(
            "Hard failures have low recovery potential."
        )

    # ---------------------------------
    # INCIDENT ADJUSTMENT
    # ---------------------------------

    if case.incident_detected:

        probability += 0.10

        reasons.append(
            "Known infrastructure incident increases likelihood of recovery."
        )

    # ---------------------------------
    # CHECKOUT ABANDONMENT
    # ---------------------------------

    if (
        case.case_type
        == "CHECKOUT_ABANDONMENT"
    ):

        probability += 0.05

        reasons.append(
            "Customer can potentially be re-engaged."
        )

    # ---------------------------------
    # LIMIT
    # ---------------------------------

    probability = min(
        probability,
        0.95
    )

    probability = max(
        probability,
        0.01
    )

    return {
        "recovery_probability":
            round(
                probability,
                2
            ),

        "reason":
            " ".join(
                reasons
            )
    }