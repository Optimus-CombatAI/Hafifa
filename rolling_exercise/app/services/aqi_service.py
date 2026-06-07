from calculate_aqi import calculate_aqi
from app.constants.config import settings
from app.schemas.air_quality import AqiResult


def calculate_aqi_data(pm25:float,no2:float,co2:float)->AqiResult:
    aqi, aqi_level = calculate_aqi(pm25,no2,co2)
    is_alert:bool = aqi > settings.alert_aqi_threshold
    return AqiResult(
        aqi=float(aqi),
        aqi_level=str(aqi_level),
        is_alert=bool(is_alert)
    )
    