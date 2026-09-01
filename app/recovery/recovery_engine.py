from sqlalchemy.orm import Session

from app.models import RecoveryCase

from app.recovery.opportunity_score import (
    calculate_opportunity_score
)

from app.recovery.probability import (
    calculate_recovery_probability
)

from app.recovery.expected_value import (
    calculate_expected_recovery_value
)

from app.recovery.ai_diagnosis import (
    diagnose_case
)

from app.recovery.decision_engine import (
    recommend_recovery_action
)


def analyze_recovery_case(
    case: RecoveryCase
) -> dict:
    """
    Run the complete Phase 3 intelligence pipeline
    for a single recovery case.
    """

    # ---------------------------------
    # 1. OPPORTUNITY SCORE
    # ---------------------------------

    opportunity_result = (
        calculate_opportunity_score(
            case
        )
    )

    opportunity_score = (
        opportunity_result[
            "opportunity_score"
        ]
    )

    # ---------------------------------
    # 2. RECOVERY PROBABILITY
    # ---------------------------------

    probability_result = (
        calculate_recovery_probability(
            case
        )
    )

    recovery_probability = (
        probability_result[
            "recovery_probability"
        ]
    )

    # ---------------------------------
    # 3. EXPECTED RECOVERY VALUE
    # ---------------------------------

    value_result = (
        calculate_expected_recovery_value(
            case,
            recovery_probability
        )
    )

    expected_recovery_value = (
        value_result[
            "expected_recovery_value"
        ]
    )

    # ---------------------------------
    # 4. AI DIAGNOSIS
    # ---------------------------------

    ai_result = (
        diagnose_case(
            case
        )
    )

    # ---------------------------------
    # 5. FINAL DECISION
    # ---------------------------------

    decision = (
        recommend_recovery_action(
            case=case,

            opportunity_score=
                opportunity_score,

            recovery_probability=
                recovery_probability,

            expected_recovery_value=
                expected_recovery_value,

            ai_diagnosis=
                ai_result
        )
    )

    # ---------------------------------
    # 6. UPDATE DATABASE OBJECT
    # ---------------------------------

    case.opportunity_score = (
        opportunity_score
    )

    case.recovery_probability = (
        recovery_probability
    )

    case.expected_recovery_value = (
        expected_recovery_value
    )

    case.ai_diagnosis = (
        ai_result[
            "diagnosis"
        ]
    )

    case.ai_confidence = (
        ai_result[
            "confidence"
        ]
    )

    case.recommended_action = (
        decision[
            "action"
        ]
    )

    case.action_reason = (
        decision[
            "reason"
        ]
    )

    case.priority = (
        decision[
            "priority"
        ]
    )

    case.intelligence_status = (
        "COMPLETED"
    )

    return {
        "case_id":
            case.case_id,

        "classification":
            case.classification,

        "opportunity_score":
            opportunity_score,

        "recovery_probability":
            recovery_probability,

        "expected_recovery_value":
            expected_recovery_value,

        "ai_diagnosis":
            ai_result[
                "diagnosis"
            ],

        "ai_confidence":
            ai_result[
                "confidence"
            ],

        "recommended_action":
            decision[
                "action"
            ],

        "priority":
            decision[
                "priority"
            ],

        "reason":
            decision[
                "reason"
            ]
    }


def process_recovery_intelligence(
    db: Session
) -> dict:
    """
    Process all recovery cases that have not yet
    completed Phase 3 intelligence.
    """

    cases = (
        db.query(
            RecoveryCase
        )
        .filter(
            RecoveryCase.intelligence_status
            != "COMPLETED"
        )
        .all()
    )

    results = []

    for case in cases:

        result = (
            analyze_recovery_case(
                case
            )
        )

        results.append(
            result
        )

    db.commit()

    return {
        "cases_analyzed":
            len(results),

        "results":
            results
    }