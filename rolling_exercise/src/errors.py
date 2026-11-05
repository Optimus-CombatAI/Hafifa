class InvalidCsvFileError(Exception):
    """The uploaded file can't be used, so none of its rows are saved."""


class CityNotFoundError(Exception):
    def __init__(self, city: str):
        super().__init__(f"No air quality data for {city}")
