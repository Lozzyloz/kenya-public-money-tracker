from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.core.roles import ADMINISTRATOR, REVIEWERS
from app.models import (
    AuditLog, Budget, CitizenReport, County, Expenditure, Project, Sector, User,
)
from app.models.project import PROJECT_STATUSES
from app.models.report import REPORT_STATUSES
from app.schemas.dashboard import (
    BudgetYearTotal, CountyCount, DashboardOut, FinanceStats, ProjectStats,
    RecentActivity, RecentProject, ReportStats, SectorCount, StatusCount,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

FINANCE_NOTE = (
    "Budget totals add up each project's current approved or revised budget "
    "(a revision replaces the figure it supersedes) by financial year. Committed "
    "funds are excluded. Projects with no budget data are not counted as zero. "
    "Expenditure is not totalled because year-to-date figures cannot be summed."
)


@router.get("", response_model=DashboardOut)
def dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*REVIEWERS)),
):
    active = Project.is_archived.is_(False)

    # ---- projects ----
    total_projects = db.scalar(select(func.count()).select_from(Project).where(active))

    county_rows = db.execute(
        select(County.id, County.name, func.count(Project.id))
        .join(Project, Project.county_id == County.id)
        .where(active)
        .group_by(County.id, County.name, County.code)
        .order_by(County.code)
    ).all()

    sector_names = dict(db.execute(select(Sector.id, Sector.name)).all())
    sector_rows = db.execute(
        select(Project.sector_id, func.count()).where(active).group_by(Project.sector_id)
    ).all()
    by_sector = sorted(
        (
            SectorCount(
                id=sector_id,
                name=sector_names.get(sector_id, "Unspecified"),
                count=count,
            )
            for sector_id, count in sector_rows
        ),
        key=lambda item: (-item.count, item.name),
    )

    status_counts = dict(
        db.execute(
            select(Project.status, func.count()).where(active).group_by(Project.status)
        ).all()
    )

    # ---- reports ----
    report_counts = dict(
        db.execute(
            select(CitizenReport.status, func.count()).group_by(CitizenReport.status)
        ).all()
    )
    public_reports = db.scalar(
        select(func.count()).select_from(CitizenReport).where(CitizenReport.is_public.is_(True))
    )

    # ---- finance ----
    superseded = select(Budget.supersedes_id).where(Budget.supersedes_id.is_not(None))
    counts_toward_totals = (
        Budget.budget_type.in_(("approved", "revised")),
        Budget.id.not_in(superseded),
    )
    budget_rows = db.execute(
        select(
            Budget.financial_year,
            func.sum(Budget.amount),
            func.count(distinct(Budget.project_id)),
        )
        .select_from(Budget)
        .join(Project, Project.id == Budget.project_id)
        .where(active, *counts_toward_totals)
        .group_by(Budget.financial_year)
        .order_by(Budget.financial_year.desc())
    ).all()

    with_budget = db.scalar(
        select(func.count(distinct(Budget.project_id)))
        .select_from(Budget)
        .join(Project, Project.id == Budget.project_id)
        .where(active, Budget.budget_type.in_(("approved", "revised")))
    )
    with_expenditure = db.scalar(
        select(func.count(distinct(Expenditure.project_id)))
        .select_from(Expenditure)
        .join(Project, Project.id == Expenditure.project_id)
        .where(active)
    )

    # ---- recent ----
    recent_projects = db.scalars(
        select(Project).where(active).order_by(Project.id.desc()).limit(5)
    ).all()

    recent_activity = None
    if user.role == ADMINISTRATOR:
        recent_activity = [
            RecentActivity.model_validate(row, from_attributes=True)
            for row in db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(10))
        ]

    return DashboardOut(
        generated_at=datetime.now(timezone.utc),
        projects=ProjectStats(
            total=total_projects,
            by_county=[CountyCount(id=i, name=n, count=c) for i, n, c in county_rows],
            by_sector=by_sector,
            by_status=[
                StatusCount(status=s, count=status_counts.get(s, 0)) for s in PROJECT_STATUSES
            ],
        ),
        reports=ReportStats(
            total=sum(report_counts.values()),
            awaiting_review=report_counts.get("submitted", 0),
            public=public_reports,
            by_status=[
                StatusCount(status=s, count=report_counts.get(s, 0)) for s in REPORT_STATUSES
            ],
        ),
        finance=FinanceStats(
            projects_with_budget_data=with_budget,
            projects_without_budget_data=total_projects - with_budget,
            projects_with_expenditure_data=with_expenditure,
            projects_without_expenditure_data=total_projects - with_expenditure,
            current_budget_by_financial_year=[
                BudgetYearTotal(financial_year=year, total=total, project_count=count)
                for year, total, count in budget_rows
            ],
            note=FINANCE_NOTE,
        ),
        recent_projects=[
            RecentProject(
                id=p.id, name=p.name, county=p.county.name, created_at=p.created_at
            )
            for p in recent_projects
        ],
        recent_activity=recent_activity,
    )
