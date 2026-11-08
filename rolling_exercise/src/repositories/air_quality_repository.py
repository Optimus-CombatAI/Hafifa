import datetime

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import Session

from src.db.air_quality_record import AirQualityRecord
from src.models.city_average_aqi import CityAverageAqi


class AirQualityRepository:
    def __init__(self, session: Session):
        self._session = session

    def save_all(self, records: list[AirQualityRecord]):
        self._session.add_all(records)
        self._session.commit()

    def get_city_days(self, dates: set[datetime.date]) -> set[tuple[datetime.date, str]]:
        query = select(AirQualityRecord.date, AirQualityRecord.city).where(AirQualityRecord.date.in_(dates))

        return {(date, city) for date, city in self._session.execute(query)}

    def get_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> list[AirQualityRecord]:
        query = (
            select(AirQualityRecord)
            .where(AirQualityRecord.date.between(start_date, end_date))
            .order_by(AirQualityRecord.date, AirQualityRecord.city)
        )

        return list(self._session.scalars(query))

    def get_by_city(self, city: str) -> list[AirQualityRecord]:
        query = select(AirQualityRecord).where(self._is_city(city)).order_by(AirQualityRecord.date)

        return list(self._session.scalars(query))

    def get_city_aqi_average(self, city: str) -> float | None:
        return self._session.scalar(select(func.avg(AirQualityRecord.aqi)).where(self._is_city(city)))

    def get_best_cities(self, count: int) -> list[CityAverageAqi]:
        average_aqi = func.avg(AirQualityRecord.aqi).label("average_aqi")
        query = (
            select(AirQualityRecord.city, average_aqi)
            .group_by(AirQualityRecord.city)
            .order_by(average_aqi, AirQualityRecord.city)
            .limit(count)
        )

        return [CityAverageAqi(city=city, average_aqi=aqi) for city, aqi in self._session.execute(query)]

    def _is_city(self, city: str) -> ColumnElement[bool]:
        return func.lower(AirQualityRecord.city) == city.lower()
