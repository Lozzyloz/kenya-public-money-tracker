from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.schemas.admin import StrictInput
from app.schemas.project import NamedItem

ReportStatus = Literal[
    "submitted", "under_review", "awaiting_information", "verified",
    "unverified", "disputed", "rejected", "resolved",
]


class ReportInput(StrictInput):
    """Everything a citizen may send. Validated after form parsing."""

    description: str = Field(min_length=10, max_length=2000)
    observed_at: date
    latitude: Decimal | None = Field(None, ge=-90, le=90, max_digits=9, decimal_places=6)
    longitude: Decimal | None = Field(None, ge=-180, le=180, max_digits=9, decimal_places=6)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(None, pattern=r"^\+?[0-9 ()\-]{7,20}$")
    contact_consent: bool = False

    @field_validator("observed_at")
    @classmethod
    def not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("observed_at cannot be in the future")
        return value

    @model_validator(mode="after")
    def cross_checks(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be given together")
        if (self.contact_email or self.contact_phone) and not self.contact_consent:
            raise ValueError("contact_consent is required when contact details are given")
        return self


class StatusChange(StrictInput):
    status: ReportStatus
    note: str = Field(min_length=3, max_length=2000)


class VisibilityChange(StrictInput):
    is_public: bool


class ReportReceipt(BaseModel):
    id: int
    status: ReportStatus
    message: str


class AttachmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mime_type: str
    size_bytes: int


class HistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    from_status: str | None
    to_status: str
    reviewer_id: int | None
    note: str | None
    changed_at: datetime


class ReportListItem(BaseModel):
    """Review queue row. No contact details here on purpose."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    project: NamedItem
    status: ReportStatus
    is_public: bool
    observed_at: date
    created_at: datetime
    attachment_count: int
    description: str


class ReportList(BaseModel):
    items: list[ReportListItem]
    total: int
    page: int
    page_size: int


class ReportReviewOut(BaseModel):
    """Full record for reviewers, including contact details."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    project: NamedItem
    description: str
    observed_at: date
    latitude: Decimal | None
    longitude: Decimal | None
    contact_email: str | None
    contact_phone: str | None
    contact_consent: bool
    reporter_user_id: int | None
    status: ReportStatus
    is_public: bool
    created_at: datetime
    attachments: list[AttachmentOut]
    history: list[HistoryOut]


class PublicReportOut(BaseModel):
    id: int
    reported_on: date
    observed_at: date
    description: str
    status: ReportStatus
    notice: str
    has_evidence: bool


class PublicReportList(BaseModel):
    has_data: bool
    items: list[PublicReportOut]
