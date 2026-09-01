import requests

from config import API_BASE_URL, REQUEST_TIMEOUT


def _get(url):
    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def _post(url):
    response = requests.post(
        url,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


# ============================================================
# HEALTH
# ============================================================

def get_health():
    return _get(
        f"{API_BASE_URL}/health"
    )


# ============================================================
# OBSERVABILITY
# ============================================================

def get_observability_summary():
    return _get(
        f"{API_BASE_URL}/observability/summary"
    )


def get_prometheus_metrics():
    response = requests.get(
        f"{API_BASE_URL}/metrics",
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.text


# ============================================================
# RECOVERY CASES
# ============================================================

def get_recovery_cases():
    return _get(
        f"{API_BASE_URL}/recovery-cases"
    )


def execute_case(case_id):
    return _post(
        f"{API_BASE_URL}/recovery/test-latency/{case_id}"
    )


# ============================================================
# PIPELINE
# ============================================================

def run_pipeline():
    return _post(
        f"{API_BASE_URL}/pipeline/process"
    )


# ============================================================
# FAILURE LAB
# ============================================================

def inject_failure(failure_name):
    return _post(
        f"{API_BASE_URL}/demo/failure/{failure_name}"
    )


def reset_failures():
    return _post(
        f"{API_BASE_URL}/demo/reset"
    )


def get_failure_state():
    return _get(
        f"{API_BASE_URL}/demo/failure-state"
    )