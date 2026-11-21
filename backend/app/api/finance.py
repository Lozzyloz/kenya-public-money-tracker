from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.core.roles import STAFF_ADMIN
from app.models import Budget, Document, Expenditure, Project, User
from app.schemas.admin import BudgetCreate, ExpenditureCreate
from app.schemas.finance import (
    BudgetList, BudgetOut, ExpenditureList, ExpenditureOut,
)
from app.services.audit import save_new

router = APIRouter(prefix="/projects", tags=["finance"])
admin_required = require_roles(*STAFF_ADMIN)


def _require_project(db: Session, project_id: int) -> None:
    project = db.get(Project, project_id)
    if project is None or project.is_archived:
        raise HTTPException(status_code=404, detail="Project not found")


def _require_document(db: Session, document_id: int) -> None:
    if db.get(Document, document_id) is None:
        raise HTTPException(status_code=422, detail="source_document_id does not exist")


@router.get("/{project_id}/budgets", response_model=BudgetList)
def list_budgets(project_id: int, db: Session = Depends(get_db)):
    _require_project(db, project_id)
    rows = db.scalars(
        select(Budget)
        .where(Budget.project_id == project_id)
        .order_by(Budget.financial_year.desc(), Budget.id)
    ).all()

    superseded = {b.supersedes_id for b in rows if b.supersedes_id is not None}
    items = []
    for row in rows:
        item = BudgetOut.model_validate(row)
        item.is_current = row.id not in superseded
        items.append(item)
    return BudgetList(has_data=bool(items), items=items)


@router.post("/{project_id}/budgets", response_model=BudgetOut, status_code=201)
def add_budget(
    project_id: int,
    payload: BudgetCreate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_required),
):
    _require_project(db, project_id)
    _require_document(db, payload.source_document_id)

    if payload.budget_type == "revised":
        if payload.supersedes_id is None:
            raise HTTPException(
                status_code=422,
                detail="A revised budget must say which budget it supersedes",
            )
        previous = db.get(Budget, payload.supersedes_id)
        if previous is None or previous.project_id != project_id:
            raise HTTPException(
                status_code=422, detail="supersedes_id must be a budget of this project"
            )
        if previous.budget_type == "committed":
            raise HTTPException(status_code=422, detail="Committed funds cannot be revised")
        if previous.financial_year != payload.financial_year:
            raise HTTPException(
                status_code=422,
                detail="A revision must be in the same financial year as the original",
            )
        already = db.scalar(select(Budget.id).where(Budget.supersedes_id == previous.id))
        if already is not None:
            raise HTTPException(
                status_code=409, detail="That budget has already been superseded"
            )
    elif payload.supersedes_id is not None:
        raise HTTPException(
            status_code=422, detail="Only a revised budget can supersede another"
        )

    return save_new(db, user, Budget(project_id=project_id, **payload.model_dump()))


@router.get("/{project_id}/expenditures", response_model=ExpenditureList)
def list_expenditures(project_id: int, db: Session = Depends(get_db)):
    _require_project(db, project_id)
    rows = db.scalars(
        select(Expenditure)
        .where(Expenditure.project_id == project_id)
        .order_by(Expenditure.period_end.desc(), Expenditure.id)
    ).all()
    items = [ExpenditureOut.model_validate(r) for r in rows]
    return ExpenditureList(has_data=bool(items), items=items)


@router.post(
    "/{project_id}/expenditures", response_model=ExpenditureOut, status_code=201
)
def add_expenditure(
    project_id: int,
    payload: ExpenditureCreate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_required),
):
    _require_project(db, project_id)
    _require_document(db, payload.source_document_id)
    return save_new(
        db, user, Expenditure(project_id=project_id, **payload.model_dump())
    )
