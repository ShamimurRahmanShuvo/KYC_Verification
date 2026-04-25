from app.models.kyc_model import AuditLog


def log_audit_event(db, action, entity_type, entity_id, user_id, details=None):
    audit_event = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        details=details
    )
    db.add(audit_event)
    db.commit()


def log_decision(db, user_id, decision_type, decision_value, reason=None):
    audit_event = AuditLog(
        action="decision",
        entity_type="user",
        entity_id=user_id,
        user_id=user_id,
        details={
            "decision_type": decision_type,
            "decision_value": decision_value,
            "reason": reason
        }
    )
    db.add(audit_event)
    db.commit()


def log_admin_action(db, admin_id, action_type, target_user_id, details=None):
    audit_event = AuditLog(
        action=action_type,
        entity_type="admin_action",
        entity_id=target_user_id,
        user_id=admin_id,
        details=details
    )
    db.add(audit_event)
    db.commit()
