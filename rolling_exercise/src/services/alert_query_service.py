import datetime

from src.models.alert_response import AlertResponse
from src.repositories.alert_repository import AlertRepository


class AlertQueryService:
    def __init__(self, alert_repository: AlertRepository):
        self._alert_repository = alert_repository

    def get_all(self) -> list[AlertResponse]:
        return [AlertResponse.model_validate(alert) for alert in self._alert_repository.get_all()]

    def get_by_date(self, date: datetime.date) -> list[AlertResponse]:
        return [AlertResponse.model_validate(alert) for alert in self._alert_repository.get_by_date(date)]

    def get_by_city(self, city: str) -> list[AlertResponse]:
        return [AlertResponse.model_validate(alert) for alert in self._alert_repository.get_by_city(city)]
