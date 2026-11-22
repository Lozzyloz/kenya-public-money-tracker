from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.admin import StrictInput, WriteVerification
from app.schemas.project import SourceDocumentOut

MilestoneStatus = Literal["pending", "in_progress", "done", "delayed"]


class MilestoneCreate(StrictInput):
    title: str = Field(min_length=1, max_length=300)
    description: str | None = Field(None, max_length=5000)
    planned_date: date | None = None
    actual_date: date | None = None
    status: MilestoneStatus = "pending"
    sort_order: int = Field(0, ge=0, le=10000)
    evidence_document_id: int | None = None


class MilestoneUpdate(StrictInput):
    title: str | None = Field(None, min_length=1, max_length=300)
    description: str | None = Field(None, max_length=5000)
    planned_date: date | None = None
    actual_date: date | None = None
    status: MilestoneStatus | None = None
    sort_order: int | None = Field(None, ge=0, le=10000)
    evidence_document_id: int | None = None

    @model_validator(mode="after")
    def required_fields_not_null(self):
        for field in ("title", "status", "sort_order"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class ProgressUpdateCreate(StrictInput):
    update_date: date
    summary: str = Field(min_length=1, max_length=5000)
    milestone_id: int | None = None
    # Only accepted together with a source document (credible assessment).
    percent_complete: int | None = Field(None, ge=0, le=100)
    source_document_id: int | None = None
    verification_status: WriteVerification | None = None

    @field_validator("update_date")
    @classmethod
    def not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("update_date cannot be in the future")
        return value

    @model_validator(mode="after")
    def evidence_rules(self):
        if self.percent_complete is not None and self.source_document_id is None:
            raise ValueError("percent_complete requires a source_document_id")
        if self.source_document_id is None and self.verification_status in (
            "official",
            "verified",
        ):
            raise ValueError(
                "an update without a source document cannot be official or verified"
            )
        return self


class MilestoneOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    planned_date: date | None
    actual_date: date | None
    status: MilestoneStatus
    sort_order: int
    evidence_document: SourceDocumentOut | None


class MilestoneList(BaseModel):
    has_data: bool
    items: list[MilestoneOut]


class ProgressUpdateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    milestone_id: int | None
    update_date: date
    summary: str
    percent_complete: int | None
    verification_status: str
    source_document: SourceDocumentOut | None


class ProgressUpdateList(BaseModel):
    has_data: bool
    items: list[ProgressUpdateOut]
