from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import (
    AfterValidator, AnyHttpUrl, BaseModel, ConfigDict, Field, model_validator,
)

from app.schemas.project import ProjectStatus

# Admins may record these. "citizen_submitted" is reserved for citizen reports.
WriteVerification = Literal["official", "verified", "unverified", "disputed"]
DocumentType = Literal[
    "budget", "implementation_report", "audit", "tender_notice", "award", "other"
]
BudgetType = Literal["approved", "revised", "committed"]


def _consecutive_years(value: str) -> str:
    first, second = value.split("/")
    if int(second) != int(first) + 1:
        raise ValueError("financial year must span consecutive years, e.g. 2025/2026")
    return value


FinancialYear = Annotated[
    str, Field(pattern=r"^\d{4}/\d{4}$"), AfterValidator(_consecutive_years)
]
Money = Annotated[
    Decimal, Field(ge=0, max_digits=18, decimal_places=2, allow_inf_nan=False)
]


def check_dates(start, expected, actual) -> None:
    if start and expected and expected < start:
        raise ValueError("expected_completion cannot be before start_date")
    if start and actual and actual < start:
        raise ValueError("actual_completion cannot be before start_date")


class StrictInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class DocumentCreate(StrictInput):
    title: str = Field(min_length=1, max_length=300)
    source_name: str = Field(min_length=1, max_length=200)
    url: AnyHttpUrl | None = None
    document_type: DocumentType
    financial_year: FinancialYear | None = None
    period_label: str | None = Field(None, max_length=50)
    published_date: date | None = None


class ContractorCreate(StrictInput):
    name: str = Field(min_length=1, max_length=200)
    registration_no: str | None = Field(None, max_length=100)


class AgencyCreate(StrictInput):
    name: str = Field(min_length=1, max_length=200)
    county_id: int | None = None


class ProjectCreate(StrictInput):
    name: str = Field(min_length=1, max_length=300)
    description: str | None = Field(None, max_length=5000)
    county_id: int
    sub_county: str | None = Field(None, max_length=100)
    location_text: str | None = Field(None, max_length=300)
    latitude: Decimal | None = Field(None, ge=-90, le=90, max_digits=9, decimal_places=6)
    longitude: Decimal | None = Field(None, ge=-180, le=180, max_digits=9, decimal_places=6)
    sector_id: int | None = None
    agency_id: int | None = None
    contractor_id: int | None = None
    start_date: date | None = None
    expected_completion: date | None = None
    actual_completion: date | None = None
    status: ProjectStatus = "unknown"
    verification_status: WriteVerification = "official"
    source_document_id: int

    @model_validator(mode="after")
    def dates_in_order(self):
        check_dates(self.start_date, self.expected_completion, self.actual_completion)
        return self


NOT_NULLABLE = (
    "name", "county_id", "status", "verification_status",
    "source_document_id", "is_archived",
)


class ProjectUpdate(StrictInput):
    name: str | None = Field(None, min_length=1, max_length=300)
    description: str | None = Field(None, max_length=5000)
    county_id: int | None = None
    sub_county: str | None = Field(None, max_length=100)
    location_text: str | None = Field(None, max_length=300)
    latitude: Decimal | None = Field(None, ge=-90, le=90, max_digits=9, decimal_places=6)
    longitude: Decimal | None = Field(None, ge=-180, le=180, max_digits=9, decimal_places=6)
    sector_id: int | None = None
    agency_id: int | None = None
    contractor_id: int | None = None
    start_date: date | None = None
    expected_completion: date | None = None
    actual_completion: date | None = None
    status: ProjectStatus | None = None
    verification_status: WriteVerification | None = None
    source_document_id: int | None = None
    is_archived: bool | None = None

    @model_validator(mode="after")
    def required_fields_not_null(self):
        for field in NOT_NULLABLE:
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class BudgetCreate(StrictInput):
    budget_type: BudgetType
    amount: Money
    financial_year: FinancialYear
    reporting_period: str | None = Field(None, max_length=50)
    source_document_id: int
    verification_status: WriteVerification = "official"
    supersedes_id: int | None = None
    notes: str | None = Field(None, max_length=2000)


class ExpenditureCreate(StrictInput):
    amount: Money
    financial_year: FinancialYear
    period_start: date | None = None
    period_end: date
    is_cumulative: bool  # required on purpose: never guess year-to-date vs period
    source_document_id: int
    verification_status: WriteVerification = "official"
    notes: str | None = Field(None, max_length=2000)

    @model_validator(mode="after")
    def period_in_order(self):
        if self.period_start and self.period_start > self.period_end:
            raise ValueError("period_start cannot be after period_end")
        return self
