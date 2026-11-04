import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.db.air_quality_record import AirQualityRecord


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    air_quality_record_id: Mapped[int] = mapped_column(ForeignKey("air_quality_records.id"), unique=True)
    date: Mapped[datetime.date]
    city: Mapped[str]
    aqi: Mapped[float]

    air_quality_record: Mapped["AirQualityRecord"] = relationship(back_populates="alert")
