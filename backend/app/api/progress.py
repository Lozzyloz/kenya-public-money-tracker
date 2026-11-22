from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.core.roles import STAFF_ADMIN
from app.models import Document, Milestone, ProgressUpdate, Project, User
from app.schemas.progress import (
    MilestoneCreate, MilestoneList, MilestoneOut, MilestoneUpdate,
    ProgressUpdateCreate, ProgressUpdateList, ProgressUpdateOut,
)
from app.services.audit import log_action, save_new, snapshot

router = APIRouter(prefix="/projects", tags=["progress"])
admin_required = require_roles(*STAFF_ADMIN)


def _project_or_404(db: Session, project_id: int) -> None:
    project = db.get(Project, project_id)
    if project is None or project.is_archived:
        raise HTTPException(status_code=404, detail="Project not found")


def _document_or_422(db: Session, document_id: int | None, field: str) -> None:
    if document_id is not None and db.get(Document, document_id) is None:
        raise HTTPException(status_code=422, detail=f"{field} {document_id} does not exist")


# ---- milestones -------------------------------------------------------

@router.get("/{project_id}/milestones", response_model=MilestoneList)
def list_milestones(project_id: int, db: Session = Depends(get_db)):
    _project_or_404(db, project_id)
    rows = db.scalars(
        select(Milestone)
        .where(Milestone.project_id == project_id)
        .order_by(Milestone.sort_order, Milestone.id)
    ).all()
    return MilestoneList(
        has_data=bool(rows), items=[MilestoneOut.model_validate(r) for r in rows]
    )


@router.post("/{project_id}/milestones", response_model=MilestoneOut, status_code=201)
def add_milestone(
    project_id: int,
    payload: MilestoneCreate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_required),
):
    _project_or_404(db, project_id)
    _document_or_422(db, payload.evidence_document_id, "evidence_document_id")
    return save_new(db, user, Milestone(project_id=project_id, **payload.model_dump()))


@router.patch("/{project_id}/milestones/{milestone_id}", response_model=MilestoneOut)
def update_milestone(
    project_id: int,
    milestone_id: int,
    payload: MilestoneUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_required),
):
    _project_or_404(db, project_id)
    milestone = db.get(Milestone, milestone_id)
    if milestone is None or milestone.project_id != project_id:
        raise HTTPException(status_code=404, detail="Milestone not found")

    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="No fields to update")
    _document_or_422(db, changes.get("evidence_document_id"), "evidence_document_id")

    before = snapshot(milestone)
    for field, value in changes.items():
        setattr(milestone, field, value)
    db.flush()
    db.refresh(milestone)
    log_action(db, user, "update", milestone, before)
    db.commit()
    db.refresh(milestone)
    return milestone


# ---- progress updates (append-only) -----------------------------------

@router.get("/{project_id}/progress-updates", response_model=ProgressUpdateList)
def list_progress_updates(project_id: int, db: Session = Depends(get_db)):
    _project_or_404(db, project_id)
    rows = db.scalars(
        select(ProgressUpdate)
        .where(ProgressUpdate.project_id == project_id)
        .order_by(ProgressUpdate.update_date.desc(), ProgressUpdate.id.desc())
    ).all()
    return ProgressUpdateList(
        has_data=bool(rows), items=[ProgressUpdateOut.model_validate(r) for r in rows]
    )


@router.post(
    "/{project_id}/progress-updates", response_model=ProgressUpdateOut, status_code=201
)
def add_progress_update(
    project_id: int,
    payload: ProgressUpdateCreate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_required),
):
    _project_or_404(db, project_id)
    _document_or_422(db, payload.source_document_id, "source_document_id")
    if payload.milestone_id is not None:
        milestone = db.get(Milestone, payload.milestone_id)
        if milestone is None or milestone.project_id != project_id:
            raise HTTPException(
                status_code=422, detail="milestone_id must be a milestone of this project"
            )

    data = payload.model_dump()
    if data["verification_status"] is None:
        data["verification_status"] = (
            "official" if data["source_document_id"] else "unverified"
        )
    return save_new(db, user, ProgressUpdate(project_id=project_id, **data))
