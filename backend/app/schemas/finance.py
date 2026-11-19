from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.schemas.project import SourceDocumentOut


class BudgetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    budget_type: str
    amount: Decimal
    financial_year: str
    reporting_period: str | None
    verification_status: str
    supersedes_id: int | None
    is_current: bool = True
    notes: str | None
    source_document: SourceDocumentOut


class ExpenditureOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    financial_year: str
    period_start: date | None
    period_end: date
    is_cumulative: bool
    verification_status: str
    notes: str | None
    source_document: SourceDocumentOut


class BudgetList(BaseModel):
    has_data: bool
    items: list[BudgetOut]


class ExpenditureList(BaseModel):
    has_data: bool
    items: list[ExpenditureOut]
