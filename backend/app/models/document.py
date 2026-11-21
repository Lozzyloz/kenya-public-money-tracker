from datetime import date, datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

DOCUMENT_TYPES = (
    "budget", "implementation_report", "audit",
    "tender_notice", "award", "other",
)


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint(
            "document_type IN ('budget','implementation_report','audit',"
            "'tender_notice','award','other')",
            name="ck_documents_type",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    source_name: Mapped[str] = mapped_column(String(200))
    url: Mapped[str | None] = mapped_column(Text)
    document_type: Mapped[str] = mapped_column(String(30))
    financial_year: Mapped[str | None] = mapped_column(String(9))
    period_label: Mapped[str | None] = mapped_column(String(50))
    published_date: Mapped[date | None]
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())
    recorded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
