from datetime import date, datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.document import Document
from app.models.finance import VERIFICATION_CHECK


class Milestone(TimestampMixin, Base):
    __tablename__ = "milestones"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','in_progress','done','delayed')",
            name="ck_milestones_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str | None] = mapped_column(Text)
    planned_date: Mapped[date | None]
    actual_date: Mapped[date | None]
    status: Mapped[str] = mapped_column(String(20))
    sort_order: Mapped[int] = mapped_column(default=0)
    evidence_document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id")
    )
    recorded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    evidence_document: Mapped[Document | None] = relationship()


class ProgressUpdate(Base):
    """Append-only. A correction is a new update, never an edit."""

    __tablename__ = "progress_updates"
    __table_args__ = (
        CheckConstraint(
            "percent_complete IS NULL OR (percent_complete BETWEEN 0 AND 100)",
            name="ck_progress_percent_range",
        ),
        CheckConstraint(
            "percent_complete IS NULL OR source_document_id IS NOT NULL",
            name="ck_progress_percent_needs_source",
        ),
        CheckConstraint(VERIFICATION_CHECK, name="ck_progress_verification"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    milestone_id: Mapped[int | None] = mapped_column(ForeignKey("milestones.id"))
    update_date: Mapped[date]
    summary: Mapped[str] = mapped_column(Text)
    percent_complete: Mapped[int | None]
    source_document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id")
    )
    verification_status: Mapped[str] = mapped_column(String(20))
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())
    recorded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    source_document: Mapped[Document | None] = relationship()
