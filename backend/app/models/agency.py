from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Agency(TimestampMixin, Base):
    __tablename__ = "agencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    county_id: Mapped[int | None] = mapped_column(ForeignKey("counties.id"))
