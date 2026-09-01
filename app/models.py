
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Date
from sqlalchemy import JSON
from sqlalchemy import Float
from sqlalchemy import Boolean
from sqlalchemy.sql import func
from app.database import Base


# ============================================================
# PAYMENT EVENTS
# ============================================================

class PaymentEvent(Base):
    __tablename__ = "payment_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    event_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    merchant_id = Column(
        String,
        nullable=False,
        index=True
    )

    event_type = Column(
        String,
        nullable=False,
        index=True
    )

    payment_id = Column(
        String,
        nullable=True,
        index=True
    )

    status = Column(
        String,
        nullable=False,
        index=True
    )

    amount = Column(
        Integer,
        nullable=True
    )

    payload = Column(
        JSON,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


# ============================================================
# CHECKOUT SESSIONS
# ============================================================

class CheckoutSession(Base):
    __tablename__ = "checkout_sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    session_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    merchant_id = Column(
        String,
        nullable=False,
        index=True
    )

    customer_id = Column(
        String,
        nullable=False,
        index=True
    )

    amount = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String,
        nullable=False,
        index=True
    )

    started_at = Column(
        DateTime(timezone=True),
        nullable=False
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    session_metadata = Column(
        JSON,
        nullable=True
    )


# ============================================================
# RECOVERY CASES
# ============================================================

class RecoveryCase(Base):
    __tablename__ = "recovery_cases"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    case_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    merchant_id = Column(
        String,
        nullable=False,
        index=True
    )

    customer_id = Column(
        String,
        nullable=True,
        index=True
    )

    payment_id = Column(
        String,
        nullable=True,
        index=True
    )

    checkout_id = Column(
        String,
        nullable=True,
        index=True
    )

    case_type = Column(
        String,
        nullable=False,
        index=True
    )

    amount = Column(
        Integer,
        nullable=False
    )

    currency = Column(
        String,
        nullable=False,
        default="INR"
    )

    revenue_at_risk = Column(
        Integer,
        nullable=False
    )

    failure_reason = Column(
        String,
        nullable=True,
        index=True
    )

    classification = Column(
        String,
        nullable=False,
        index=True
    )

    confidence = Column(
        Float,
        nullable=False
    )

    classification_reason = Column(
        String,
        nullable=True
    )


# ========================================================
# INCIDENT INTELLIGENCE
# ========================================================

    incident_type = Column(
        String,
        nullable=True,
        index=True
    )

    incident_provider = Column(
        String,
        nullable=True,
        index=True
    )

    incident_detected = Column(
        Boolean,
        nullable=False,
        default=False
    )

    routing = Column(
        String,
        nullable=False,
        index=True
    )


# ========================================================
# PHASE 3 — RECOVERY INTELLIGENCE
# ========================================================

    recommended_action = Column(
        String,
        nullable=False
    )

    opportunity_score = Column(
        Float,
        nullable=True,
        index=True
    )

    recovery_probability = Column(
        Float,
        nullable=True
    )

    expected_recovery_value = Column(
        Float,
        nullable=True
    )

    ai_diagnosis = Column(
        String,
        nullable=True
    )

    ai_confidence = Column(
        Float,
        nullable=True
    )

    action_reason = Column(
        String,
        nullable=True
    )

    priority = Column(
        String,
        nullable=True,
        index=True
    )

    intelligence_status = Column(
        String,
        nullable=False,
        default="PENDING",
        index=True
    )


# ========================================================
# PHASE 4 — GUARDRAILS
# ========================================================

    customer_consent = Column(
        Boolean,
        nullable=True,
        default=True
    )

    recovered = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True
    )

    recovered_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    execution_status = Column(
        String,
        nullable=False,
        default="PENDING",
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    retry_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    max_retries = Column(
        Integer,
        nullable=False,
        default=3
    )


# ========================================================
# PHASE 5 — RECOVERY OUTCOME STATUS
# ========================================================

    recovery_status = Column(
        String,
        nullable=False,
        default="AT_RISK",
        index=True
    )


# ============================================================
# PHASE 4 — RECOVERY ACTION LOG
# ============================================================

class RecoveryActionLog(Base):
    __tablename__ = "recovery_action_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    case_id = Column(
        String,
        nullable=False,
        index=True
    )

    merchant_id = Column(
        String,
        nullable=False,
        index=True
    )

    customer_id = Column(
        String,
        nullable=True,
        index=True
    )

    action = Column(
        String,
        nullable=False,
        index=True
    )

    status = Column(
        String,
        nullable=False,
        index=True
    )

    block_reason = Column(
        String,
        nullable=True
    )

    estimated_cost = Column(
        Float,
        nullable=False,
        default=0
    )
    latency_seconds = Column(
    Float,
    nullable=True
  )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )


# ============================================================
# PHASE 4 — CIRCUIT BREAKER
# ============================================================

class CircuitBreakerState(Base):
    __tablename__ = "circuit_breaker_states"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    provider = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    state = Column(
        String,
        nullable=False,
        default="CLOSED"
    )

    failure_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    failure_threshold = Column(
        Integer,
        nullable=False,
        default=5
    )

    opened_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    cooldown_seconds = Column(
        Integer,
        nullable=False,
        default=300
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )


# ============================================================
# PHASE 4 — RECOVERY BUDGET
# ============================================================

class RecoveryBudget(Base):
    __tablename__ = "recovery_budgets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    merchant_id = Column(
        String,
        nullable=False,
        index=True
    )

    budget_date = Column(
        Date,
        nullable=False,
        index=True
    )

    daily_limit = Column(
        Float,
        nullable=False,
        default=10000
    )

    spent = Column(
        Float,
        nullable=False,
        default=0
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


# ============================================================
# PHASE 5 — RECOVERY OUTCOMES
# ============================================================

class RecoveryOutcome(Base):
    __tablename__ = "recovery_outcomes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    case_id = Column(
        String,
        nullable=False,
        index=True
    )

    merchant_id = Column(
        String,
        nullable=False,
        index=True
    )

    payment_id = Column(
        String,
        nullable=True,
        index=True
    )

    checkout_id = Column(
        String,
        nullable=True,
        index=True
    )

    action = Column(
        String,
        nullable=False,
        index=True
    )

    status = Column(
        String,
        nullable=False,
        default="PENDING",
        index=True
    )

    amount = Column(
        Integer,
        nullable=False
    )

    recovered_amount = Column(
        Integer,
        nullable=False,
        default=0
    )

    failure_reason = Column(
        String,
        nullable=True
    )

    payment_link = Column(
        String,
        nullable=True
    )

    message_status = Column(
        String,
        nullable=True
    )

    outcome_metadata = Column(
        JSON,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )


# ============================================================
# PHASE 7 — AUDIT TRAIL
# ============================================================

class RecoveryAuditLog(Base):
    __tablename__ = "recovery_audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    case_id = Column(
        String,
        nullable=False,
        index=True
    )

    merchant_id = Column(
        String,
        nullable=False,
        index=True
    )

    event_type = Column(
        String,
        nullable=False,
        index=True
    )

    event_source = Column(
        String,
        nullable=False
    )

    decision = Column(
        String,
        nullable=True
    )

    reasoning = Column(
        String,
        nullable=True
    )

    guardrail_result = Column(
        JSON,
        nullable=True
    )

    execution_result = Column(
        JSON,
        nullable=True
    )

    audit_metadata = Column(
        JSON,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )


# ============================================================
# PHASE 7 — RECOVERY POSTMORTEMS
# ============================================================

class RecoveryPostmortem(Base):
    __tablename__ = "recovery_postmortems"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    case_id = Column(
        String,
        nullable=False,
        index=True
    )

    merchant_id = Column(
        String,
        nullable=False,
        index=True
    )

    failure_stage = Column(
        String,
        nullable=False,
        index=True
    )

    attempted_action = Column(
        String,
        nullable=True,
        index=True
    )

    failure_reason = Column(
        String,
        nullable=True
    )

    root_cause = Column(
        String,
        nullable=True
    )

    ai_diagnosis = Column(
        String,
        nullable=True
    )

    guardrail_result = Column(
        JSON,
        nullable=True
    )

    execution_result = Column(
        JSON,
        nullable=True
    )

    recovery_status = Column(
        String,
        nullable=False,
        index=True
    )

    recovered_amount = Column(
        Integer,
        nullable=False,
        default=0
    )

    recommended_followup = Column(
        String,
        nullable=True
    )

    postmortem_metadata = Column(
        JSON,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

