
from datetime import date


class DuplicateDataException(Exception):

    def __init__(self, city_name: str, error_date: date):
        message = f"For the city {city_name} a report on {error_date} already exists!"
        super().__init__(message)
        self.city_name = city_name
        self.error_date = error_date

    def __str__(self):
        return f"For the city {self.city_name} a report on {self.error_date} already exists!"
