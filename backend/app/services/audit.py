from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.models import AuditLog, User


def _plain(value):
    # Money becomes a string so the audit trail keeps exact figures.
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def snapshot(obj) -> dict:
    return {
        attr.key: _plain(getattr(obj, attr.key))
        for attr in inspect(obj).mapper.column_attrs
    }


def log_action(db: Session, user: User, action: str, obj, before: dict | None = None):
    """Adds the audit row to the current transaction; the caller commits."""
    db.add(
        AuditLog(
            user_id=user.id,
            action=action,
            table_name=obj.__tablename__,
            record_id=obj.id,
            before=before,
            after=snapshot(obj),
        )
    )


def save_new(db: Session, user: User, obj):
    """Insert a record, stamp who recorded it and log it, in one transaction."""
    if hasattr(obj, "recorded_by"):
        obj.recorded_by = user.id
    db.add(obj)
    db.flush()
    db.refresh(obj)
    log_action(db, user, "create", obj)
    db.commit()
    db.refresh(obj)
    return obj
