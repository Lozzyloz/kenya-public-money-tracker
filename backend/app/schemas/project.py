from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict

ProjectStatus = Literal[
    "planned", "ongoing", "completed", "delayed",
    "suspended", "stalled", "unknown",
]


class NamedItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class SourceDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    source_name: str
    url: str | None
    document_type: str
    financial_year: str | None
    period_label: str | None
    published_date: date | None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    county: NamedItem
    sub_county: str | None
    location_text: str | None
    sector: NamedItem | None
    agency: NamedItem | None
    contractor: NamedItem | None
    start_date: date | None
    expected_completion: date | None
    actual_completion: date | None
    status: ProjectStatus
    verification_status: str
    source_document: SourceDocumentOut


class ProjectList(BaseModel):
    items: list[ProjectOut]
    total: int
    page: int
    page_size: int
