from sqlalchemy.orm import Session

from app.models import RecoveryActionLog


def get_guardrail_summary(
    db: Session
) -> dict:

    logs = (
        db.query(
            RecoveryActionLog
        )
        .all()
    )

    executed = 0
    blocked = 0
    escalated = 0
    failed = 0

    for log in logs:

        if log.status == "EXECUTED":

            executed += 1

        elif log.status == "BLOCKED":

            blocked += 1

        elif log.status == "ESCALATED":

            escalated += 1

        elif log.status == "FAILED":

            failed += 1

    return {
        "total_action_attempts":
            len(logs),

        "executed":
            executed,

        "blocked":
            blocked,

        "escalated":
            escalated,

        "failed":
            failed
    }