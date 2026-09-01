
"""
Phase 6 — Failure Injection

These helpers intentionally simulate infrastructure
and application failures so that resilience behavior
can be tested safely.
"""


class GatewayOutageError(Exception):
    """Simulated payment gateway outage."""
    pass


class LLMFailureError(Exception):
    """Simulated LLM/service failure."""
    pass


class DuplicateEventError(Exception):
    """Simulated duplicate event."""
    pass


class RetryExhaustedError(Exception):
    """Simulated retry exhaustion."""
    pass


def inject_gateway_outage():
    """
    Simulate a payment gateway outage.
    """
    raise GatewayOutageError(
        "Payment gateway is unavailable."
    )


def inject_llm_failure():
    """
    Simulate an LLM/service failure.
    """
    raise LLMFailureError(
        "LLM service is unavailable."
    )


def inject_duplicate_event():
    """
    Simulate duplicate event detection.
    """
    raise DuplicateEventError(
        "Duplicate payment event detected."
    )


def inject_retry_exhaustion():
    """
    Simulate retry exhaustion.
    """
    raise RetryExhaustedError(
        "Maximum retry attempts exhausted."
    )

