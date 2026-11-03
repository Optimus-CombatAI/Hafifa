import logging

from calculate_aqi import calculate_aqi
from src.models.aqi_result import AqiResult

logger = logging.getLogger(__name__)


class AqiCalculator:
    """Wraps the given calculate_aqi function so it returns a typed result and can be mocked in tests."""

    def calculate(self, pm25: float, no2: float, co2: float) -> AqiResult:
        aqi, aqi_level = calculate_aqi(pm25, no2, co2)
        logger.info(f"Calculated AQI {aqi} ({aqi_level}) for PM2.5={pm25}, NO2={no2}, CO2={co2}")

        return AqiResult(aqi=aqi, aqi_level=aqi_level)
