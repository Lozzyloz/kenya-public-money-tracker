from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.agency import Agency
from app.models.base import Base, TimestampMixin
from app.models.contractor import Contractor
from app.models.county import County
from app.models.document import Document
from app.models.sector import Sector

PROJECT_STATUSES = (
    "planned", "ongoing", "completed", "delayed",
    "suspended", "stalled", "unknown",
)
VERIFICATION_STATUSES = (
    "official", "verified", "citizen_submitted", "unverified", "disputed",
)


class Project(TimestampMixin, Base):
    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint(
            "status IN ('planned','ongoing','completed','delayed',"
            "'suspended','stalled','unknown')",
            name="ck_projects_status",
        ),
        CheckConstraint(
            "verification_status IN ('official','verified','citizen_submitted',"
            "'unverified','disputed')",
            name="ck_projects_verification",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(300))
    description: Mapped[str | None] = mapped_column(Text)

    county_id: Mapped[int] = mapped_column(ForeignKey("counties.id"), index=True)
    sub_county: Mapped[str | None] = mapped_column(String(100))
    location_text: Mapped[str | None] = mapped_column(String(300))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))

    sector_id: Mapped[int | None] = mapped_column(ForeignKey("sectors.id"), index=True)
    agency_id: Mapped[int | None] = mapped_column(ForeignKey("agencies.id"))
    contractor_id: Mapped[int | None] = mapped_column(ForeignKey("contractors.id"))

    start_date: Mapped[date | None]
    expected_completion: Mapped[date | None]
    actual_completion: Mapped[date | None]

    status: Mapped[str] = mapped_column(String(20), index=True)
    verification_status: Mapped[str] = mapped_column(String(20))
    source_document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    recorded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    county: Mapped[County] = relationship()
    sector: Mapped[Sector | None] = relationship()
    agency: Mapped[Agency | None] = relationship()
    contractor: Mapped[Contractor | None] = relationship()
    source_document: Mapped[Document] = relationship()
