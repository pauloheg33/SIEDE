from sqlalchemy.orm import Session
from app.models import AuditLog
from uuid import UUID
from typing import Optional


def log_action(
    db: Session,
    user_id: UUID,
    action: str,
    entity: str,
    entity_id: str,
    details: Optional[dict] = None
):
    """Create an audit log entry"""
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        details=details or {}
    )
    db.add(audit_log)
    db.commit()
