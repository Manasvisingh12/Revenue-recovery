from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import RecoveryActionLog


MAX_CONTACTS_PER_DAY = 2


def check_contact_limit(
    db: Session,
    case
) -> dict:

    if case.recommended_action != "MESSAGE":

        return {
            "allowed": True,
            "reason":
                "Contact limit does not apply."
        }

    if not case.customer_id:

        return {
            "allowed": False,
            "reason":
                "Customer ID is required for contact."
        }

    now = datetime.now(
        timezone.utc
    )

    start_of_day = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    contact_count = (
        db.query(
            RecoveryActionLog
        )
        .filter(
            RecoveryActionLog.customer_id
            == case.customer_id,

            RecoveryActionLog.action
            == "MESSAGE",

            RecoveryActionLog.status
            == "EXECUTED",

            RecoveryActionLog.created_at
            >= start_of_day
        )
        .count()
    )

    if contact_count >= MAX_CONTACTS_PER_DAY:

        return {
            "allowed": False,

            "reason":
                f"Daily contact limit exceeded. "
                f"Maximum contacts per day: "
                f"{MAX_CONTACTS_PER_DAY}.",

            "contact_count":
                contact_count
        }

    return {
        "allowed": True,

        "reason":
            f"Contact {contact_count + 1} "
            f"of {MAX_CONTACTS_PER_DAY} allowed.",

        "contact_count":
            contact_count
    }