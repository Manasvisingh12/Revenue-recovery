
from app.failure_engineering.failure_injector import (
    inject_gateway_outage,
    inject_llm_failure,
    inject_duplicate_event,
    inject_retry_exhaustion,
)


def test_gateway_outage():

    try:
        inject_gateway_outage()

    except Exception as e:

        return {
            "failure": "GATEWAY_OUTAGE",
            "caught": True,
            "safe_state": "STOP"
        }


def test_llm_failure():

    try:
        inject_llm_failure()

    except Exception as e:

        return {
            "failure": "LLM_FAILURE",
            "caught": True,
            "safe_state": "FALLBACK"
        }


def test_duplicate_event():

    try:
        inject_duplicate_event()

    except Exception as e:

        return {
            "failure": "DUPLICATE_EVENT",
            "caught": True,
            "safe_state": "NO_ACTION"
        }


def test_retry_exhaustion():

    try:
        inject_retry_exhaustion()

    except Exception as e:

        return {
            "failure": "RETRY_EXHAUSTION",
            "caught": True,
            "safe_state": "ESCALATE"
        }


def run_failure_tests():

    return [
        test_gateway_outage(),
        test_llm_failure(),
        test_duplicate_event(),
        test_retry_exhaustion(),
    ]

