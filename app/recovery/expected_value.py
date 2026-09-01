def calculate_expected_recovery_value(
    case,
    recovery_probability: float
) -> dict:
    """
    Calculate expected revenue that can
    realistically be recovered.
    """

    amount = (
        case.revenue_at_risk
        or case.amount
        or 0
    )

    expected_value = (
        amount
        * recovery_probability
    )

    return {
        "revenue_at_risk":
            amount,

        "recovery_probability":
            recovery_probability,

        "expected_recovery_value":
            round(
                expected_value,
                2
            )
    }