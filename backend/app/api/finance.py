from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Budget, Expenditure, Project
from app.schemas.finance import (
    BudgetList, BudgetOut, ExpenditureList, ExpenditureOut,
)

router = APIRouter(prefix="/projects", tags=["finance"])


def _require_project(db: Session, project_id: int) -> None:
    project = db.get(Project, project_id)
    if project is None or project.is_archived:
        raise HTTPException(status_code=404, detail="Project not found")


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
