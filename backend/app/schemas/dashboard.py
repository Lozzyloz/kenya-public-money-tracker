from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class CountyCount(BaseModel):
    id: int
    name: str
    count: int


class SectorCount(BaseModel):
    id: int | None  # None = projects with no sector recorded
    name: str
    count: int


class StatusCount(BaseModel):
    status: str
    count: int


class ProjectStats(BaseModel):
    total: int
    by_county: list[CountyCount]
    by_sector: list[SectorCount]
    by_status: list[StatusCount]


class ReportStats(BaseModel):
    total: int
    awaiting_review: int
    public: int
    by_status: list[StatusCount]


class BudgetYearTotal(BaseModel):
    financial_year: str
    total: Decimal
    project_count: int


class FinanceStats(BaseModel):
    projects_with_budget_data: int
    projects_without_budget_data: int
    projects_with_expenditure_data: int
    projects_without_expenditure_data: int
    current_budget_by_financial_year: list[BudgetYearTotal]
    note: str


class RecentProject(BaseModel):
    id: int
    name: str
    county: str
    created_at: datetime


class RecentActivity(BaseModel):
    id: int
    user_id: int
    action: str
    table_name: str
    record_id: int
    created_at: datetime


class DashboardOut(BaseModel):
    generated_at: datetime
    projects: ProjectStats
    reports: ReportStats
    finance: FinanceStats
    recent_projects: list[RecentProject]
    recent_activity: list[RecentActivity] | None  # administrators only
