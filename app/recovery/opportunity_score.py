from datetime import datetime, timezone


def calculate_opportunity_score(case) -> dict:
    """
    Calculate a 0-100 recovery opportunity score.

    The score represents how attractive this case
    is for automated recovery.
    """

    score = 0

    reasons = []

    # ---------------------------------
    # 1. TRANSACTION VALUE
    # Maximum: 30 points
    # ---------------------------------

    amount = case.amount or 0

    if amount >= 10000:

        score += 30

        reasons.append(
            "High transaction value."
        )

    elif amount >= 5000:

        score += 25

        reasons.append(
            "Moderately high transaction value."
        )

    elif amount >= 2000:

        score += 20

        reasons.append(
            "Medium transaction value."
        )

    elif amount >= 500:

        score += 10

        reasons.append(
            "Low-to-medium transaction value."
        )

    else:

        score += 5

        reasons.append(
            "Low transaction value."
        )

    # ---------------------------------
    # 2. FAILURE CLASSIFICATION
    # Maximum: 30 points
    # ---------------------------------

    classification = case.classification

    if classification == "SOFT_FAILURE":

        score += 30

        reasons.append(
            "Soft failures are highly recoverable."
        )

    elif classification == "SYSTEM_FAILURE":

        score += 25

        reasons.append(
            "System failure may recover after retry."
        )

    elif classification == "AMBIGUOUS":

        score += 15

        reasons.append(
            "Failure is ambiguous and requires analysis."
        )

    elif classification == "HARD_FAILURE":

        score += 2

        reasons.append(
            "Hard failure has low recovery potential."
        )

    # ---------------------------------
    # 3. INCIDENT INTELLIGENCE
    # Maximum: 20 points
    # ---------------------------------

    if case.incident_detected:

        score += 20

        reasons.append(
            "Infrastructure incident detected."
        )

    # ---------------------------------
    # 4. CASE RECENCY
    # Maximum: 20 points
    # ---------------------------------

    if case.created_at:

        now = datetime.now(
            timezone.utc
        )

        created_at = case.created_at

        if created_at.tzinfo is None:

            created_at = created_at.replace(
                tzinfo=timezone.utc
            )

        age_minutes = (
            now - created_at
        ).total_seconds() / 60

        if age_minutes <= 10:

            score += 20

            reasons.append(
                "Very recent recovery opportunity."
            )

        elif age_minutes <= 60:

            score += 15

            reasons.append(
                "Recent recovery opportunity."
            )

        elif age_minutes <= 1440:

            score += 10

            reasons.append(
                "Recovery opportunity is less than 24 hours old."
            )

        else:

            score += 5

            reasons.append(
                "Recovery opportunity is older."
            )

    # ---------------------------------
    # CAP SCORE
    # ---------------------------------

    score = min(
        score,
        100
    )

    return {
        "opportunity_score": score,
        "reason": " ".join(
            reasons
        )
    }