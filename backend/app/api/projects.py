from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.core.roles import STAFF_ADMIN
from app.models import Agency, Contractor, County, Document, Project, Sector, User
from app.schemas.admin import ProjectCreate, ProjectUpdate, check_dates
from app.schemas.project import ProjectList, ProjectOut, ProjectStatus
from app.services.audit import log_action, save_new, snapshot

router = APIRouter(prefix="/projects", tags=["projects"])
admin_required = require_roles(*STAFF_ADMIN)

REFERENCES = {
    "county_id": County,
    "sector_id": Sector,
    "agency_id": Agency,
    "contractor_id": Contractor,
    "source_document_id": Document,
}


def _check_references(db: Session, data: dict) -> None:
    for field, model in REFERENCES.items():
        value = data.get(field)
        if value is not None and db.get(model, value) is None:
            raise HTTPException(status_code=422, detail=f"{field} {value} does not exist")


@router.get("", response_model=ProjectList)
def list_projects(
    county_id: int | None = None,
    sector_id: int | None = None,
    status: ProjectStatus | None = None,
    q: str | None = Query(None, min_length=2, max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    stmt = select(Project).where(Project.is_archived.is_(False))
    if county_id:
        stmt = stmt.where(Project.county_id == county_id)
    if sector_id:
        stmt = stmt.where(Project.sector_id == sector_id)
    if status:
        stmt = stmt.where(Project.status == status)
    if q:
        stmt = stmt.where(Project.name.ilike(f"%{q}%"))

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.scalars(
        stmt.order_by(Project.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return ProjectList(items=items, total=total, page=page, page_size=page_size)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if project is None or project.is_archived:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_required),
):
    data = payload.model_dump()
    _check_references(db, data)
    return save_new(db, user, Project(**data))


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_required),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="No fields to update")
    _check_references(db, changes)
    try:
        check_dates(
            changes.get("start_date", project.start_date),
            changes.get("expected_completion", project.expected_completion),
            changes.get("actual_completion", project.actual_completion),
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

    before = snapshot(project)
    for field, value in changes.items():
        setattr(project, field, value)
    db.flush()
    db.refresh(project)
    action = "archive" if changes.get("is_archived") is True else "update"
    log_action(db, user, action, project, before)
    db.commit()
    db.refresh(project)
    return project
