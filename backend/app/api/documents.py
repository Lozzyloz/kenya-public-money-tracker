from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.core.roles import STAFF_ADMIN
from app.models import Document, User
from app.schemas.admin import DocumentCreate
from app.schemas.project import SourceDocumentOut
from app.services.audit import save_new

router = APIRouter(prefix="/documents", tags=["documents"])
admin_required = require_roles(*STAFF_ADMIN)


@router.get("", response_model=list[SourceDocumentOut])
def list_documents(
    q: str | None = Query(None, min_length=2, max_length=100),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(Document)
    if q:
        stmt = stmt.where(Document.title.ilike(f"%{q}%"))
    return db.scalars(stmt.order_by(Document.id.desc()).limit(limit)).all()


@router.post("", response_model=SourceDocumentOut, status_code=201)
def create_document(
    payload: DocumentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_required),
):
    data = payload.model_dump()
    data["url"] = str(data["url"]) if data["url"] else None
    return save_new(db, user, Document(**data))
