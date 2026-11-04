import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.db.alert import Alert


class AlertRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_all(self) -> list[Alert]:
        return list(self._session.scalars(select(Alert).order_by(Alert.date, Alert.city)))

    def get_by_date(self, date: datetime.date) -> list[Alert]:
        return list(self._session.scalars(select(Alert).where(Alert.date == date).order_by(Alert.city)))

    def get_by_city(self, city: str) -> list[Alert]:
        query = select(Alert).where(func.lower(Alert.city) == city.lower()).order_by(Alert.date)

        return list(self._session.scalars(query))
