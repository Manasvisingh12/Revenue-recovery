from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import (
    RecoveryCase,
    RecoveryActionLog,
)


MAX_CONTACTS_24H = 2


def check_contact_limit(
    db: Session,
    case: RecoveryCase
) -> dict:
    """
    Prevent excessive customer contact.
    """

    if not case.customer_id:

        return {
            "allowed": False,
            "reason": "CUSTOMER_ID_REQUIRED"
        }

    since = datetime.utcnow() - timedelta(
        hours=24
    )

    contact_count = db.query(
        RecoveryActionLog
    ).filter(
        RecoveryActionLog.customer_id
        == case.customer_id,

        RecoveryActionLog.action
        == "MESSAGE",

        RecoveryActionLog.status
        == "EXECUTED",

        RecoveryActionLog.created_at
        >= since
    ).count()

    if contact_count >= MAX_CONTACTS_24H:

        return {
            "allowed": False,
            "reason": "CONTACT_LIMIT_EXCEEDED"
        }

    return {
        "allowed": True,
        "reason": None
    }