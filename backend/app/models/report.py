from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean, CheckConstraint, ForeignKey, Numeric, String, Text, false, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.project import Project

REPORT_STATUSES = (
    "submitted", "under_review", "awaiting_information", "verified",
    "unverified", "disputed", "rejected", "resolved",
)
STATUS_LIST = ",".join(f"'{s}'" for s in REPORT_STATUSES)


class ReportAttachment(Base):
    __tablename__ = "report_attachments"
    __table_args__ = (
        CheckConstraint(
            "mime_type IN ('image/jpeg','image/png','application/pdf')",
            name="ck_attachments_mime",
        ),
        CheckConstraint("size_bytes > 0", name="ck_attachments_size"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("citizen_reports.id"), index=True)
    # Server-generated name. The client's filename is never stored or used.
    stored_name: Mapped[str] = mapped_column(String(64), unique=True)
    mime_type: Mapped[str] = mapped_column(String(50))
    size_bytes: Mapped[int]
    uploaded_at: Mapped[datetime] = mapped_column(server_default=func.now())


class ReportStatusHistory(Base):
    __tablename__ = "report_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("citizen_reports.id"), index=True)
    from_status: Mapped[str | None] = mapped_column(String(30))
    to_status: Mapped[str] = mapped_column(String(30))
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    note: Mapped[str | None] = mapped_column(Text)
    changed_at: Mapped[datetime] = mapped_column(server_default=func.now())


class CitizenReport(TimestampMixin, Base):
    __tablename__ = "citizen_reports"
    __table_args__ = (
        CheckConstraint(f"status IN ({STATUS_LIST})", name="ck_reports_status"),
        CheckConstraint(
            "contact_consent OR (contact_email IS NULL AND contact_phone IS NULL)",
            name="ck_reports_contact_needs_consent",
        ),
        CheckConstraint(
            "NOT is_public OR status NOT IN ('submitted','rejected')",
            name="ck_reports_public_needs_review",
        ),
        CheckConstraint(
            "(latitude IS NULL) = (longitude IS NULL)",
            name="ck_reports_coordinates_paired",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    reporter_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    description: Mapped[str] = mapped_column(Text)
    observed_at: Mapped[date]
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    contact_email: Mapped[str | None] = mapped_column(String(255))
    contact_phone: Mapped[str | None] = mapped_column(String(30))
    contact_consent: Mapped[bool] = mapped_column(Boolean, server_default=false())
    status: Mapped[str] = mapped_column(String(30), index=True)
    is_public: Mapped[bool] = mapped_column(Boolean, server_default=false())

    project: Mapped[Project] = relationship()
    attachments: Mapped[list[ReportAttachment]] = relationship(
        order_by=ReportAttachment.id, lazy="selectin"
    )
    history: Mapped[list[ReportStatusHistory]] = relationship(
        order_by=ReportStatusHistory.id, lazy="selectin"
    )

    @property
    def attachment_count(self) -> int:
        return len(self.attachments)
