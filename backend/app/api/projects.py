from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Project
from app.schemas.project import ProjectList, ProjectOut, ProjectStatus

router = APIRouter(prefix="/projects", tags=["projects"])


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
