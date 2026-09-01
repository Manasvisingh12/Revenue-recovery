from sqlalchemy.orm import Session
from app.models import RecoveryAuditLog

def record_audit_event(db: Session, case, event_type: str, event_source: str, decision: str = None, reasoning: str = None, guardrail_result: dict = None, execution_result: dict = None, metadata: dict = None):
    audit = RecoveryAuditLog(
        case_id=case.case_id,
        merchant_id=case.merchant_id,
        event_type=event_type,
        event_source=event_source,
        decision=decision,
        reasoning=reasoning,
        guardrail_result=guardrail_result,
        execution_result=execution_result,
        audit_metadata=metadata,
    )
    db.add(audit)
    db.flush()
    return audit

def get_case_timeline(db: Session, case_id: str):
    return (
        db.query(RecoveryAuditLog)
        .filter(RecoveryAuditLog.case_id == case_id)
        .order_by(RecoveryAuditLog.created_at.asc(), RecoveryAuditLog.id.asc())
        .all()
    )

def build_case_timeline(db: Session, case_id: str):
    events = get_case_timeline(db, case_id)
    return [
        {
            'timestamp': event.created_at,
            'event_type': event.event_type,
            'source': event.event_source,
            'decision': event.decision,
            'reasoning': event.reasoning,
            'guardrail_result': event.guardrail_result,
            'execution_result': event.execution_result,
            'metadata': event.audit_metadata,
        }
        for event in events
    ]
