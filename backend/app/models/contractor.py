from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Contractor(TimestampMixin, Base):
    __tablename__ = "contractors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    registration_no: Mapped[str | None] = mapped_column(String(100))
