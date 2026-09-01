failure_state = {
    "gateway_failure": False,
    "llm_failure": False,
    "duplicate_event": False,
    "recovery_exhaustion": False,
}


def set_failure(name, enabled=True):
    if name not in failure_state:
        raise ValueError(
            f"Unknown failure: {name}"
        )

    failure_state[name] = enabled


def get_failure_state():
    return failure_state.copy()


def reset_failures():
    for key in failure_state:
        failure_state[key] = False