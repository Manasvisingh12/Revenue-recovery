
"""
Phase 6 — Failure Handlers

Every injected failure must result in a safe state.
"""


def handle_gateway_outage(case):
    """
    Gateway unavailable.

    Never continue blindly with payment execution.
    """

    case.execution_status = "BLOCKED"

    return {
        "failure": "GATEWAY_OUTAGE",
        "status": "SAFE",
        "action": "STOP",
        "reason": "PAYMENT_GATEWAY_UNAVAILABLE"
    }


def handle_llm_failure(case):
    """
    LLM unavailable.

    Do not invent an AI recommendation.
    Fall back to a deterministic safe action.
    """

    case.intelligence_status = "FALLBACK"

    case.recommended_action = "WAIT"

    return {
        "failure": "LLM_FAILURE",
        "status": "SAFE",
        "action": "WAIT",
        "reason": "LLM_UNAVAILABLE_RULE_BASED_FALLBACK"
    }


def handle_duplicate_event(case):
    """
    Duplicate event.

    Do not create another recovery action.
    """

    case.execution_status = "BLOCKED"

    return {
        "failure": "DUPLICATE_EVENT",
        "status": "SAFE",
        "action": "NO_ACTION",
        "reason": "DUPLICATE_EVENT_IGNORED"
    }


def handle_retry_exhaustion(case):
    """
    Retry limit reached.

    Stop automated retries and escalate.
    """

    case.execution_status = "ESCALATED"

    return {
        "failure": "RETRY_EXHAUSTION",
        "status": "SAFE",
        "action": "ESCALATE",
        "reason": "MAX_RETRIES_REACHED"
    }

