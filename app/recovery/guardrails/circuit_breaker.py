
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import CircuitBreakerState


DEFAULT_PROVIDER = "GLOBAL"


def get_or_create_circuit_breaker(
    db: Session,
    provider: str
):
    """
    Get the circuit breaker for a provider.
    Create one if it does not exist.
    """

    breaker = (
        db.query(
            CircuitBreakerState
        )
        .filter(
            CircuitBreakerState.provider
            == provider
        )
        .first()
    )

    if breaker:
        return breaker

    breaker = CircuitBreakerState(
        provider=provider,
        state="CLOSED",
        failure_count=0,
        failure_threshold=5,
        cooldown_seconds=300
    )

    db.add(breaker)
    db.flush()

    return breaker


def check_circuit_breaker(
    db: Session,
    case
) -> dict:
    """
    Check whether automated recovery is allowed
    for the provider associated with the case.
    """

    # ------------------------------------------------
    # Determine provider
    # ------------------------------------------------

    provider = (
        case.incident_provider
        or DEFAULT_PROVIDER
    )

    # ------------------------------------------------
    # Get provider circuit breaker
    # ------------------------------------------------

    breaker = (
        get_or_create_circuit_breaker(
            db,
            provider
        )
    )

    # ------------------------------------------------
    # CLOSED
    # ------------------------------------------------

    if breaker.state == "CLOSED":

        return {
            "allowed": True,
            "reason":
                "Circuit breaker is closed.",
            "state":
                "CLOSED"
        }

    # ------------------------------------------------
    # OPEN
    # ------------------------------------------------

    if breaker.state == "OPEN":

        now = datetime.now(
            timezone.utc
        )

        opened_at = breaker.opened_at

        if opened_at:

            if opened_at.tzinfo is None:

                opened_at = (
                    opened_at.replace(
                        tzinfo=timezone.utc
                    )
                )

            elapsed = (
                now - opened_at
            ).total_seconds()

            # ----------------------------------------
            # Cooldown completed
            # ----------------------------------------

            if (
                elapsed
                >= breaker.cooldown_seconds
            ):

                breaker.state = "HALF_OPEN"

                return {
                    "allowed": True,
                    "reason":
                        "Circuit breaker entered HALF_OPEN state.",
                    "state":
                        "HALF_OPEN"
                }

        # --------------------------------------------
        # Still inside cooldown
        # --------------------------------------------

        return {
            "allowed": False,
            "reason":
                "Circuit breaker is OPEN. "
                "Automated action is temporarily blocked.",
            "state":
                "OPEN"
        }

    # ------------------------------------------------
    # HALF OPEN
    # ------------------------------------------------

    if breaker.state == "HALF_OPEN":

        return {
            "allowed": True,
            "reason":
                "Circuit breaker allows a controlled test action.",
            "state":
                "HALF_OPEN"
        }

    # ------------------------------------------------
    # UNKNOWN STATE
    # ------------------------------------------------

    return {
        "allowed": False,
        "reason":
            "Unknown circuit breaker state.",
        "state":
            breaker.state
    }


def record_action_success(
    db: Session,
    provider: str
):
    """
    Successful action resets the circuit breaker.
    """

    breaker = (
        get_or_create_circuit_breaker(
            db,
            provider
        )
    )

    breaker.failure_count = 0
    breaker.state = "CLOSED"
    breaker.opened_at = None


def record_action_failure(
    db: Session,
    provider: str
):
    """
    Failed actions increase the failure count.
    The circuit opens after the configured threshold.
    """

    breaker = (
        get_or_create_circuit_breaker(
            db,
            provider
        )
    )

    breaker.failure_count += 1

    if (
        breaker.failure_count
        >= breaker.failure_threshold
    ):

        breaker.state = "OPEN"

        breaker.opened_at = (
            datetime.now(
                timezone.utc
            )
        )
