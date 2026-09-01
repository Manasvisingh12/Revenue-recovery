import uuid

from app.models import RecoveryCase


def generate_recovery_payment_link(
    case: RecoveryCase
) -> str:

    token = uuid.uuid4().hex[:12]

    return (
        f"https://recovery.local/pay/"
        f"{case.case_id}/"
        f"{token}"
    )