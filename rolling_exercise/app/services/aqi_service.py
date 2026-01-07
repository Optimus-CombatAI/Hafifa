from calculate_aqi import calculate_aqi
from app.constants.aqi_constants import ALERT_AQI_THRESHOLD


def calculate_aqi_data(pm25:float,no2:float,co2:float)->dict:
    aqi, aqi_level = calculate_aqi(pm25,no2,co2)
    is_alert:bool = aqi > ALERT_AQI_THRESHOLD
    return{
        "aqi":float(aqi),
        "aqi_level":str(aqi_level),
        "is_alert": bool(is_alert)
    }
    
