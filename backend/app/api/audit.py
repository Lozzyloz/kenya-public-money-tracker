from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.core.roles import STAFF_ADMIN
from app.models import AuditLog
from app.schemas.audit import AuditLogList

router = APIRouter(
    prefix="/audit-logs",
    tags=["audit"],
    dependencies=[Depends(require_roles(*STAFF_ADMIN))],
)


@router.get("", response_model=AuditLogList)
def list_audit_logs(
    table_name: str | None = Query(None, max_length=50),
    record_id: int | None = None,
    user_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(AuditLog)
    if table_name:
        stmt = stmt.where(AuditLog.table_name == table_name)
    if record_id is not None:
        stmt = stmt.where(AuditLog.record_id == record_id)
    if user_id is not None:
        stmt = stmt.where(AuditLog.user_id == user_id)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.scalars(
        stmt.order_by(AuditLog.id.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return AuditLogList(items=items, total=total, page=page, page_size=page_size)
