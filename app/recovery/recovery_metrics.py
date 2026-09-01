from sqlalchemy.orm import Session
from sqlalchemy import func

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
)

from app.models import (
    RecoveryCase,
    RecoveryOutcome,
    RecoveryActionLog,
    CircuitBreakerState,
)


# ============================================================
# EXISTING DATABASE RECOVERY METRICS
# ============================================================

def get_recovery_metrics(
    db: Session,
) -> dict:

    total_cases = (
        db.query(RecoveryOutcome)
        .count()
    )

    successful_cases = (
        db.query(RecoveryOutcome)
        .filter(
            RecoveryOutcome.status == "SUCCESS"
        )
        .count()
    )

    failed_cases = (
        db.query(RecoveryOutcome)
        .filter(
            RecoveryOutcome.status == "FAILED"
        )
        .count()
    )

    total_at_risk = (
        db.query(
            func.coalesce(
                func.sum(
                    RecoveryOutcome.amount
                ),
                0,
            )
        )
        .scalar()
    )

    total_recovered = (
        db.query(
            func.coalesce(
                func.sum(
                    RecoveryOutcome.recovered_amount
                ),
                0,
            )
        )
        .scalar()
    )

    recovery_rate = (
        successful_cases / total_cases
        if total_cases > 0
        else 0
    )

    return {
        "total_recovery_attempts": total_cases,

        "successful_recoveries":
            successful_cases,

        "failed_recoveries":
            failed_cases,

        "revenue_at_risk":
            total_at_risk,

        "revenue_recovered":
            total_recovered,

        "recovery_rate":
            round(
                recovery_rate * 100,
                2,
            ),
    }


# ============================================================
# PROMETHEUS METRICS
# ============================================================


# ============================================================
# 1. BUSINESS METRICS
# ============================================================

revenue_at_risk = Gauge(
    "revenue_at_risk",
    "Total revenue currently at risk",
)


revenue_recovered = Gauge(
    "revenue_recovered",
    "Total revenue successfully recovered",
)


# ============================================================
# 2. RECOVERY OUTCOME METRICS
# ============================================================

recovery_attempts_total = Counter(
    "recovery_attempts_total",
    "Total number of recovery attempts",
)


recovery_success_total = Counter(
    "recovery_success_total",
    "Total number of successful recoveries",
)


recovery_failed_total = Counter(
    "recovery_failed_total",
    "Total number of failed recoveries",
)


# ============================================================
# 3. CIRCUIT BREAKER
# ============================================================

circuit_breaker_state = Gauge(
    "circuit_breaker_state",
    "Current state of the recovery circuit breaker",
)


# ============================================================
# 4. RECOVERY LATENCY
# ============================================================

recovery_latency = Histogram(
    "recovery_latency",
    "Recovery execution latency in seconds",
)


# ============================================================
# 5. AI DECISIONS
# ============================================================

ai_decisions_total = Counter(
    "ai_decisions_total",
    "Total number of AI recovery decisions",
    ["action"],
)


# ============================================================
# 6. GUARDRAIL BLOCKS
# ============================================================

guardrail_blocks_total = Counter(
    "guardrail_blocks_total",
    "Total number of recovery actions blocked by guardrails",
    ["reason"],
)


# ============================================================
# ACTION NORMALIZATION
# ============================================================

def normalize_action(action: str) -> str:

    if action is None:
        return "STOP"

    action_map = {

        "RETRY_CHECKOUT":
            "RETRY",

        "RETRY_WITH_ALTERNATE_ROUTE":
            "RETRY",

        "REQUEST_ALTERNATIVE_PAYMENT_METHOD":
            "MESSAGE",

        "REQUEST_CARD_UPDATE":
            "MESSAGE",

        "CUSTOMER_REVIEW":
            "ESCALATE",

        "AI_REVIEW":
            "ESCALATE",

        "RETRY":
            "RETRY",

        "WAIT":
            "WAIT",

        "MESSAGE":
            "MESSAGE",

        "ESCALATE":
            "ESCALATE",

        "NO_ACTION":
            "NO_ACTION",

        "STOP":
            "STOP",
    }

    return action_map.get(
        action,
        "STOP",
    )


# ============================================================
# REFRESH AI DECISION METRICS
# ============================================================

def refresh_ai_decision_metrics(
    db: Session,
) -> None:

    decision_counts = (
        db.query(
            RecoveryCase.recommended_action,
            func.count(RecoveryCase.id),
        )
        .group_by(
            RecoveryCase.recommended_action
        )
        .all()
    )

    actions = [
        "RETRY",
        "WAIT",
        "MESSAGE",
        "ESCALATE",
        "NO_ACTION",
        "STOP",
    ]

    # --------------------------------------------------------
    # Reset all known values
    # --------------------------------------------------------

    for action in actions:

        ai_decisions_total.labels(
            action=action
        )._value.set(0)

    # --------------------------------------------------------
    # Populate from PostgreSQL
    # --------------------------------------------------------

    normalized_counts = {
        action: 0
        for action in actions
    }

    for action, count in decision_counts:

        normalized_action = normalize_action(
            action
        )

        normalized_counts[
            normalized_action
        ] += count

    for action, count in normalized_counts.items():

        ai_decisions_total.labels(
            action=action
        )._value.set(
            float(count)
        )


# ============================================================
# REFRESH GUARDRAIL METRICS
# ============================================================

def refresh_guardrail_metrics(
    db: Session,
) -> None:

    blocked_counts = (
        db.query(
            RecoveryActionLog.block_reason,
            func.count(RecoveryActionLog.id),
        )
        .filter(
            RecoveryActionLog.status == "BLOCKED"
        )
        .group_by(
            RecoveryActionLog.block_reason
        )
        .all()
    )

    # --------------------------------------------------------
    # Reset existing labelled values
    # --------------------------------------------------------

    for reason, _ in blocked_counts:

        normalized_reason = (
            reason
            if reason
            else "UNKNOWN"
        )

        guardrail_blocks_total.labels(
            reason=normalized_reason
        )._value.set(0)

    # --------------------------------------------------------
    # Populate counts
    # --------------------------------------------------------

    for reason, count in blocked_counts:

        normalized_reason = (
            reason
            if reason
            else "UNKNOWN"
        )

        guardrail_blocks_total.labels(
            reason=normalized_reason
        )._value.set(
            float(count)
        )


# ============================================================
# REFRESH CIRCUIT BREAKER METRIC
# ============================================================

def refresh_circuit_breaker_metric(
    db: Session,
) -> None:

    breaker = (
        db.query(CircuitBreakerState)
        .order_by(
            CircuitBreakerState.id.desc()
        )
        .first()
    )

    if not breaker:

        circuit_breaker_state.set(0)

        return

    state_map = {

        "CLOSED": 0,

        "OPEN": 1,

        "HALF_OPEN": 2,
    }

    circuit_breaker_state.set(
        state_map.get(
            breaker.state,
            0,
        )
    )


# ============================================================
# PROMETHEUS DATABASE METRICS REFRESH
# ============================================================

def refresh_revenue_metrics(
    db: Session,
) -> None:

    """
    PostgreSQL is the source of truth for
    persisted business and recovery metrics.

    Recovery latency is intentionally NOT rebuilt
    from PostgreSQL. It is recorded directly by
    execute_recovery_action().
    """

    # ========================================================
    # REVENUE CURRENTLY AT RISK
    # ========================================================

    current_revenue_at_risk = (
        db.query(
            func.coalesce(
                func.sum(
                    RecoveryCase.revenue_at_risk
                ),
                0,
            )
        )
        .filter(
            RecoveryCase.recovered == False
        )
        .scalar()
    )

    # ========================================================
    # REVENUE ACTUALLY RECOVERED
    # ========================================================

    current_revenue_recovered = (
        db.query(
            func.coalesce(
                func.sum(
                    RecoveryOutcome.recovered_amount
                ),
                0,
            )
        )
        .scalar()
    )

    # ========================================================
    # SUCCESSFUL RECOVERIES
    # ========================================================

    successful_recoveries = (
        db.query(RecoveryOutcome)
        .filter(
            RecoveryOutcome.status == "SUCCESS"
        )
        .count()
    )

    # ========================================================
    # TOTAL RECOVERY ATTEMPTS
    # ========================================================

    recovery_attempts = (
        db.query(RecoveryOutcome)
        .count()
    )

    # ========================================================
    # FAILED RECOVERIES
    # ========================================================

    failed_recoveries = (
        db.query(RecoveryOutcome)
        .filter(
            RecoveryOutcome.status == "FAILED"
        )
        .count()
    )

    # ========================================================
    # UPDATE BUSINESS METRICS
    # ========================================================

    revenue_at_risk.set(
        float(
            current_revenue_at_risk or 0
        )
    )

    revenue_recovered.set(
        float(
            current_revenue_recovered or 0
        )
    )

    # ========================================================
    # UPDATE RECOVERY OUTCOME METRICS
    # ========================================================

    recovery_attempts_total._value.set(
        float(recovery_attempts)
    )

    recovery_success_total._value.set(
        float(successful_recoveries)
    )

    recovery_failed_total._value.set(
        float(failed_recoveries)
    )

    # ========================================================
    # UPDATE AI DECISION METRICS
    # ========================================================

    refresh_ai_decision_metrics(
        db
    )

    # ========================================================
    # UPDATE GUARDRAIL METRICS
    # ========================================================

    refresh_guardrail_metrics(
        db
    )

    # ========================================================
    # UPDATE CIRCUIT BREAKER
    # ========================================================

    refresh_circuit_breaker_metric(
        db
    )

    # ========================================================
    # IMPORTANT:
    # recovery_latency is NOT refreshed here.
    #
    # It is an application-runtime histogram and is
    # updated by execute_recovery_action().
    # ========================================================