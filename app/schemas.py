from typing import Optional
from typing import Dict
from typing import Any

from pydantic import BaseModel


class PaymentEventCreate(BaseModel):

    event_id: str

    merchant_id: str

    event_type: str

    payment_id: Optional[str] = None

    status: str

    amount: Optional[int] = None

    payload: Optional[Dict[str, Any]] = None


class PaymentEventResponse(PaymentEventCreate):

    id: int

    class Config:
        from_attributes = True

class RecoveryCaseResponse(BaseModel):

    id: int
    case_id: str

    merchant_id: str
    customer_id: Optional[str] = None

    payment_id: Optional[str] = None
    checkout_id: Optional[str] = None

    case_type: str

    amount: int
    currency: str
    revenue_at_risk: int

    failure_reason: Optional[str] = None

    classification: str
    confidence: float
    classification_reason: Optional[str] = None

    # ========================================================
    # INCIDENT INTELLIGENCE
    # ========================================================

    incident_type: Optional[str] = None
    incident_provider: Optional[str] = None
    incident_detected: bool = False

    routing: str

    # ========================================================
    # RECOVERY INTELLIGENCE
    # ========================================================

    recommended_action: str

    opportunity_score: Optional[float] = None
    recovery_probability: Optional[float] = None
    expected_recovery_value: Optional[float] = None

    ai_diagnosis: Optional[str] = None
    ai_confidence: Optional[float] = None

    action_reason: Optional[str] = None

    priority: Optional[str] = None

    intelligence_status: str

    # ========================================================
    # GUARDRAILS
    # ========================================================

    customer_consent: Optional[bool] = None

    recovered: bool = False
    recovered_at: Optional[Any] = None

    execution_status: str

    retry_count: int = 0
    max_retries: int = 3

    # ========================================================
    # PHASE 5
    # ========================================================

    recovery_status: str

    # ========================================================
    # TIMESTAMPS
    # ========================================================

    created_at: Optional[Any] = None
    updated_at: Optional[Any] = None

    class Config:
        from_attributes = True