from app.models import RecoveryCase


def check_retry_limit(
    case: RecoveryCase
) -> dict:
    """
    Prevent unlimited retry attempts.
    """

    if case.retry_count >= case.max_retries:

        return {
            "allowed": False,
            "reason": "RETRY_LIMIT_EXCEEDED"
        }

    return {
        "allowed": True,
        "reason": None
    }