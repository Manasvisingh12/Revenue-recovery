from sqlalchemy.orm import Session

from app.models import RecoveryActionLog


MAX_RETRY_ATTEMPTS = 3


def check_retry_limit(
    db: Session,
    case
) -> dict:

    if case.recommended_action != "RETRY":

        return {
            "allowed": True,
            "reason":
                "Retry limit does not apply."
        }

    retry_count = (
        db.query(
            RecoveryActionLog
        )
        .filter(
            RecoveryActionLog.case_id
            == case.case_id,

            RecoveryActionLog.action
            == "RETRY",

            RecoveryActionLog.status
            == "EXECUTED"
        )
        .count()
    )

    if retry_count >= MAX_RETRY_ATTEMPTS:

        return {
            "allowed": False,

            "reason":
                f"Retry limit exceeded. "
                f"Maximum allowed retries: "
                f"{MAX_RETRY_ATTEMPTS}.",

            "retry_count":
                retry_count
        }

    return {
        "allowed": True,

        "reason":
            f"Retry attempt {retry_count + 1} "
            f"of {MAX_RETRY_ATTEMPTS} allowed.",

        "retry_count":
            retry_count
    }