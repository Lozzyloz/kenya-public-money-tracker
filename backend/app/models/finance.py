from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean, CheckConstraint, ForeignKey, Numeric,
    String, Text, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.document import Document

VERIFICATION_CHECK = (
    "verification_status IN ('official','verified','citizen_submitted',"
    "'unverified','disputed')"
)


class Budget(Base):
    """Append-only: a revision is a new row that points at the one it replaces."""

    __tablename__ = "budgets"
    __table_args__ = (
        CheckConstraint(
            "budget_type IN ('approved','revised','committed')",
            name="ck_budgets_type",
        ),
        CheckConstraint("amount >= 0", name="ck_budgets_amount_nonneg"),
        CheckConstraint(VERIFICATION_CHECK, name="ck_budgets_verification"),
        UniqueConstraint("supersedes_id", name="uq_budgets_supersedes"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    budget_type: Mapped[str] = mapped_column(String(20))
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    financial_year: Mapped[str] = mapped_column(String(9))
    reporting_period: Mapped[str | None] = mapped_column(String(50))
    source_document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    verification_status: Mapped[str] = mapped_column(String(20))
    supersedes_id: Mapped[int | None] = mapped_column(ForeignKey("budgets.id"))
    notes: Mapped[str | None] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())
    recorded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    source_document: Mapped[Document] = relationship()


class Expenditure(Base):
    __tablename__ = "expenditures"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_expenditures_amount_nonneg"),
        CheckConstraint(VERIFICATION_CHECK, name="ck_expenditures_verification"),
        CheckConstraint(
            "period_start IS NULL OR period_start <= period_end",
            name="ck_expenditures_period_order",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    financial_year: Mapped[str] = mapped_column(String(9))
    period_start: Mapped[date | None]
    period_end: Mapped[date]
    # True when the source reports year-to-date totals, so figures from
    # different reports must never be added together.
    is_cumulative: Mapped[bool] = mapped_column(Boolean)
    source_document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    verification_status: Mapped[str] = mapped_column(String(20))
    notes: Mapped[str | None] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now())
    recorded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    source_document: Mapped[Document] = relationship()
