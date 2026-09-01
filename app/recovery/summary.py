from sqlalchemy.orm import Session

from app.models import RecoveryCase


def get_recovery_summary(
    db: Session
) -> dict:

    cases = (
        db.query(
            RecoveryCase
        )
        .filter(
            RecoveryCase.intelligence_status
            == "COMPLETED"
        )
        .all()
    )

    action_counts = {}

    total_revenue_at_risk = 0

    total_expected_recovery = 0

    for case in cases:

        action = (
            case.recommended_action
            or "UNKNOWN"
        )

        action_counts[action] = (
            action_counts.get(
                action,
                0
            )
            + 1
        )

        total_revenue_at_risk += (
            case.revenue_at_risk
            or 0
        )

        total_expected_recovery += (
            case.expected_recovery_value
            or 0
        )

    return {
        "total_cases":
            len(cases),

        "total_revenue_at_risk":
            total_revenue_at_risk,

        "total_expected_recovery":
            round(
                total_expected_recovery,
                2
            ),

        "action_distribution":
            action_counts
    }