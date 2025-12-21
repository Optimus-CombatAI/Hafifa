
from datetime import date


class DuplicateReportForCity(Exception):

    def __init__(self, city_name: str, error_date: date):
        self.message = f"For the city {city_name} a report on {error_date} already exists!"
        super().__init__(self.message)
        self.city_name = city_name
        self.error_date = error_date

    def __str__(self):
        return self.message
