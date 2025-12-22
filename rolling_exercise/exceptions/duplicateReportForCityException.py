from datetime import date
from exceptions.dbIntegrityException import DBIntegrityException


class DuplicateReportForCityException(DBIntegrityException):

    def __init__(self, city_name: str, error_date: date):
        message = f"For the city {city_name} a report on {error_date} already exists!"
        super().__init__(message)
        self.city_name = city_name
        self.error_date = error_date

    def __str__(self):
        return self.message
