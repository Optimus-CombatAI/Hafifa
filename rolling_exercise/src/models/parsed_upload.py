from pydantic import BaseModel

from src.models.air_quality_reading import AirQualityReading
from src.models.rejected_row import RejectedRow


class ParsedUpload(BaseModel):
    readings: list[AirQualityReading]
    rejected_rows: list[RejectedRow]
