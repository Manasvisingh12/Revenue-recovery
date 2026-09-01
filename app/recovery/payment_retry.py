from app.models import RecoveryCase


# ============================================================
# PHASE 5 — PAYMENT RETRY SIMULATION
# ============================================================


RETRYABLE_FAILURES = {
    "BANK_TIMEOUT",
    "GATEWAY_TIMEOUT",
    "TEMPORARY_AUTH_ERROR",
}


def simulate_payment_retry(
    case: RecoveryCase
) -> dict:
    """
    Simulate a payment retry.

    This is deterministic so the same failure
    type produces the same recovery outcome.
    """

    failure_reason = (
        case.failure_reason or ""
    ).upper()

    # ========================================================
    # RETRYABLE FAILURE
    # ========================================================

    if failure_reason in RETRYABLE_FAILURES:

        return {
            "action": "RETRY",
            "status": "SUCCESS",
            "recovered_amount": case.amount,
            "failure_reason": None,
            "message": (
                "Payment retry succeeded. "
                "Revenue recovered successfully."
            )
        }

    # ========================================================
    # NON-RETRYABLE FAILURE
    # ========================================================

    return {
        "action": "RETRY",
        "status": "FAILED",
        "recovered_amount": 0,
        "failure_reason": failure_reason,
        "message": (
            "Payment retry failed. "
            "Failure is not retryable."
        )
    }