from threading import Lock


class FailureLab:
    """
    In-memory failure injection controller for the hackathon demo.

    These flags intentionally exist only for demonstration.
    They are NOT production failure handling.
    """

    def __init__(self):
        self._lock = Lock()

        self.gateway_failure = False
        self.llm_failure = False
        self.duplicate_event = False
        self.recovery_exhaustion = False

    def inject(self, failure_name: str):

        with self._lock:

            if failure_name == "gateway":
                self.gateway_failure = True

            elif failure_name == "llm":
                self.llm_failure = True

            elif failure_name == "duplicate":
                self.duplicate_event = True

            elif failure_name == "recovery-exhaustion":
                self.recovery_exhaustion = True

            else:
                return {
                    "success": False,
                    "error": f"Unknown failure: {failure_name}",
                }

            return {
                "success": True,
                "status": "injected",
                "failure": failure_name,
            }

    def reset(self):

        with self._lock:

            self.gateway_failure = False
            self.llm_failure = False
            self.duplicate_event = False
            self.recovery_exhaustion = False

        return {
            "success": True,
            "status": "reset",
        }

    def state(self):

        with self._lock:

            return {
                "gateway_failure": self.gateway_failure,
                "llm_failure": self.llm_failure,
                "duplicate_event": self.duplicate_event,
                "recovery_exhaustion": self.recovery_exhaustion,
            }


failure_lab = FailureLab()