from sqlalchemy.orm import Session

from app.models import RecoveryCase


def check_already_recovered(
    db: Session,
    case: RecoveryCase
) -> dict:
    """
    Prevent recovery actions from being executed
    when the revenue has already been recovered.
    """

    # Primary Phase 4 recovery flag
    if case.recovered is True:

        return {
            "allowed": False,
            "reason": "ALREADY_RECOVERED"
        }

    # Also protect against legacy status values
    if getattr(case, "status", None) == "RECOVERED":

        return {
            "allowed": False,
            "reason": "ALREADY_RECOVERED"
        }

    return {
        "allowed": True,
        "reason": None
    }