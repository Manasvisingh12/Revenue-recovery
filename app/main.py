from prometheus_client import generate_latest
from prometheus_client import CONTENT_TYPE_LATEST

from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response

from sqlalchemy import func
from sqlalchemy.orm import Session

from prometheus_fastapi_instrumentator import Instrumentator

from app.database import get_db

from app.models import (
    PaymentEvent,
    RecoveryCase,
)

from app.schemas import (
    PaymentEventCreate,
    PaymentEventResponse,
    RecoveryCaseResponse,
)

from app.pipeline.batch_processor import process_batch

from app.recovery.recovery_metrics import (
    recovery_latency,
    refresh_revenue_metrics,
)


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Revenue Recovery Engine",
    description="AI-powered Revenue Reliability Engineering Platform",
    version="0.1.0",
)

Instrumentator().instrument(app)


# ============================================================
# PROMETHEUS METRICS
# ============================================================

@app.get("/metrics")
def metrics(
    db: Session = Depends(get_db),
):

    refresh_revenue_metrics(db)

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


# ============================================================
# HEALTH
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Revenue Recovery Engine is running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# PAYMENT EVENTS
# ============================================================

@app.post(
    "/events",
    response_model=PaymentEventResponse,
)
def create_event(
    event: PaymentEventCreate,
    db: Session = Depends(get_db),
):

    existing_event = (
        db.query(PaymentEvent)
        .filter(
            PaymentEvent.event_id == event.event_id
        )
        .first()
    )

    if existing_event:

        raise HTTPException(
            status_code=400,
            detail="Event already exists",
        )

    new_event = PaymentEvent(
        event_id=event.event_id,
        merchant_id=event.merchant_id,
        event_type=event.event_type,
        payment_id=event.payment_id,
        status=event.status,
        amount=event.amount,
        payload=event.payload,
    )

    db.add(new_event)

    db.commit()

    db.refresh(new_event)

    return new_event


@app.get(
    "/events",
    response_model=list[PaymentEventResponse],
)
def get_events(
    db: Session = Depends(get_db),
):

    events = (
        db.query(PaymentEvent)
        .order_by(
            PaymentEvent.id.desc()
        )
        .all()
    )

    return events


# ============================================================
# PIPELINE
# ============================================================

@app.post("/pipeline/process")
def run_pipeline(
    db: Session = Depends(get_db),
):

    result = process_batch(db)

    return {
        "status": "completed",
        "result": result,
    }


# ============================================================
# RECOVERY CASES
# ============================================================

@app.get(
    "/recovery-cases",
    response_model=list[RecoveryCaseResponse],
)
def get_recovery_cases(
    db: Session = Depends(get_db),
):

    cases = (
        db.query(RecoveryCase)
        .order_by(
            RecoveryCase.id.desc()
        )
        .all()
    )

    return cases


@app.get("/recovery-cases/summary")
def recovery_case_summary(
    db: Session = Depends(get_db),
):

    cases = (
        db.query(RecoveryCase)
        .all()
    )

    total_cases = len(cases)

    total_revenue_at_risk = sum(
        case.revenue_at_risk
        for case in cases
    )

    hard_failures = sum(
        case.classification == "HARD_FAILURE"
        for case in cases
    )

    soft_failures = sum(
        case.classification == "SOFT_FAILURE"
        for case in cases
    )

    system_failures = sum(
        case.classification == "SYSTEM_FAILURE"
        for case in cases
    )

    ambiguous = sum(
        case.classification == "AMBIGUOUS"
        for case in cases
    )

    return {
        "total_cases": total_cases,
        "total_revenue_at_risk": total_revenue_at_risk,
        "classifications": {
            "HARD_FAILURE": hard_failures,
            "SOFT_FAILURE": soft_failures,
            "SYSTEM_FAILURE": system_failures,
            "AMBIGUOUS": ambiguous,
        },
    }


# ============================================================
# RECOVERY EXECUTION
# ============================================================

@app.post("/recovery/test-latency/{case_id}")
def test_recovery_latency(
    case_id: str,
    db: Session = Depends(get_db),
):

    from app.recovery.action_executor import (
        execute_recovery_action
    )

    case = (
        db.query(RecoveryCase)
        .filter(
            RecoveryCase.case_id == case_id
        )
        .first()
    )

    if not case:

        raise HTTPException(
            status_code=404,
            detail="Recovery case not found",
        )

    result = execute_recovery_action(
        db,
        case,
    )

    db.commit()

    return {
        "case_id": case.case_id,
        "result": result,
    }


# ============================================================
# PHASE 8 — OBSERVABILITY SUMMARY
# ============================================================

@app.get("/observability/summary")
def observability_summary(
    db: Session = Depends(get_db),
):

    from app.models import (
        RecoveryOutcome,
        RecoveryActionLog,
        CircuitBreakerState,
    )

    # --------------------------------------------------------
    # REVENUE
    # --------------------------------------------------------

    revenue_at_risk = (
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

    revenue_recovered = (
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

    # --------------------------------------------------------
    # RECOVERY OUTCOMES
    # --------------------------------------------------------

    total_attempts = (
        db.query(RecoveryOutcome)
        .count()
    )

    successful = (
        db.query(RecoveryOutcome)
        .filter(
            RecoveryOutcome.status == "SUCCESS"
        )
        .count()
    )

    failed = (
        db.query(RecoveryOutcome)
        .filter(
            RecoveryOutcome.status == "FAILED"
        )
        .count()
    )

    # --------------------------------------------------------
    # RATES
    # --------------------------------------------------------

    success_rate = (
        successful / total_attempts * 100
        if total_attempts > 0
        else 0
    )

    recovery_value_rate = (
        revenue_recovered / revenue_at_risk * 100
        if revenue_at_risk > 0
        else 0
    )

    # --------------------------------------------------------
    # GUARDRAIL BLOCKS
    # --------------------------------------------------------

    guardrail_blocks = (
        db.query(RecoveryActionLog)
        .filter(
            RecoveryActionLog.status == "BLOCKED"
        )
        .count()
    )

    # --------------------------------------------------------
    # CIRCUIT BREAKER
    # --------------------------------------------------------

    breaker = (
        db.query(CircuitBreakerState)
        .order_by(
            CircuitBreakerState.id.desc()
        )
        .first()
    )

    breaker_state = (
        breaker.state
        if breaker
        else "UNKNOWN"
    )

    # --------------------------------------------------------
    # AI DECISION DISTRIBUTION
    # --------------------------------------------------------

    ai_decision_rows = (
        db.query(
            RecoveryCase.recommended_action,
            func.count(RecoveryCase.id),
        )
        .group_by(
            RecoveryCase.recommended_action
        )
        .all()
    )

    ai_decision_distribution = {
        "RETRY": 0,
        "WAIT": 0,
        "MESSAGE": 0,
        "ESCALATE": 0,
        "NO_ACTION": 0,
        "STOP": 0,
    }

    action_map = {
        "RETRY_CHECKOUT": "RETRY",
        "RETRY_WITH_ALTERNATE_ROUTE": "RETRY",

        "REQUEST_ALTERNATIVE_PAYMENT_METHOD": "MESSAGE",
        "REQUEST_CARD_UPDATE": "MESSAGE",

        "CUSTOMER_REVIEW": "ESCALATE",
        "AI_REVIEW": "ESCALATE",
    }

    for action, count in ai_decision_rows:

        if action is None:
            continue

        normalized_action = action_map.get(
            action,
            action,
        )

        if normalized_action not in ai_decision_distribution:
            normalized_action = "STOP"

        ai_decision_distribution[
            normalized_action
        ] += count

    # --------------------------------------------------------
    # LATENCY
    # --------------------------------------------------------

    latency_samples = list(
        recovery_latency.collect()[0].samples
    )

    latency_count_value = 0
    latency_sum_value = 0

    for sample in latency_samples:

        if sample.name.endswith("_count"):
            latency_count_value = sample.value

        elif sample.name.endswith("_sum"):
            latency_sum_value = sample.value

    average_latency = (
        latency_sum_value / latency_count_value
        if latency_count_value > 0
        else 0
    )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "revenue": {
            "at_risk": float(
                revenue_at_risk or 0
            ),
            "recovered": float(
                revenue_recovered or 0
            ),
        },

        "recovery": {
            "attempts": total_attempts,
            "successful": successful,
            "failed": failed,
            "success_rate_percent": round(
                success_rate,
                2,
            ),
            "recovery_value_rate_percent": round(
                recovery_value_rate,
                2,
            ),
        },

        "reliability": {
            "guardrail_blocks": guardrail_blocks,
            "circuit_breaker": breaker_state,
            "latency_count": latency_count_value,
            "latency_sum_seconds": round(
                latency_sum_value,
                6,
            ),
            "average_latency_seconds": round(
                average_latency,
                6,
            ),
        },

        "ai_decisions": ai_decision_distribution,
    }


# ============================================================
# PHASE 9 — FAILURE LAB
# ============================================================

@app.get("/demo/failure-state")
def get_demo_failure_state():

    from app.recovery.demo_state import (
        get_failure_state
    )

    return get_failure_state()


@app.post("/demo/failure/{failure_name}")
def inject_demo_failure(
    failure_name: str,
):

    from app.recovery.demo_state import (
        set_failure
    )

    allowed_failures = {
        "gateway_failure",
        "llm_failure",
        "duplicate_event",
        "recovery_exhaustion",
    }

    if failure_name not in allowed_failures:

        raise HTTPException(
            status_code=400,
            detail={
                "error": "Unknown failure scenario",
                "allowed": sorted(
                    allowed_failures
                ),
            },
        )

    set_failure(
        failure_name,
        True,
    )

    return {
        "status": "injected",
        "failure": failure_name,
    }


@app.post("/demo/reset")
def reset_demo_failures():

    from app.recovery.demo_state import (
        reset_failures
    )

    reset_failures()

    return {
        "status": "reset"
    }