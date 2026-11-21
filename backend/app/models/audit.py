from datetime import datetime

from sqlalchemy import JSON, CheckConstraint, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditLog(Base):
    """Append-only record of who changed what. Never updated or deleted."""

    __tablename__ = "audit_logs"
    __table_args__ = (
        CheckConstraint(
            "action IN ('create','update','archive')", name="ck_audit_action"
        ),
        Index("ix_audit_logs_record", "table_name", "record_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(20))
    table_name: Mapped[str] = mapped_column(String(50))
    record_id: Mapped[int]
    before: Mapped[dict | None] = mapped_column(JSON)
    after: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
