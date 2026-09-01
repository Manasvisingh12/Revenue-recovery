from enum import Enum


class FailureClassification(str, Enum):

    HARD_FAILURE = "HARD_FAILURE"

    SOFT_FAILURE = "SOFT_FAILURE"

    SYSTEM_FAILURE = "SYSTEM_FAILURE"

    AMBIGUOUS = "AMBIGUOUS"