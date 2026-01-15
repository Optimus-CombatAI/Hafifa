from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.air_quality import AirQualityMeasurementOut
from app.db.models import AirQualityMeasurement
from app.constants.config import settings


router = APIRouter()

@router.get("/alerts",response_model=list[AirQualityMeasurementOut])
async def get_alerts(db:AsyncSession = Depends(get_db))->list[AirQualityMeasurementOut]:
    alerts_query = select(AirQualityMeasurement).where(AirQualityMeasurement.aqi > settings.alert_aqi_threshold)
    result = await db.execute(alerts_query)
    alerts = result.scalars().all()
    if not alerts:
        return []

    return alerts

@router.get("/alerts/city/{city}",response_model=list[AirQualityMeasurementOut])
async def get_alerts_by_city(city:str,db:AsyncSession = Depends(get_db))->list[AirQualityMeasurementOut]:
    alerts_city_by_city_query = select(AirQualityMeasurement).where(AirQualityMeasurement.aqi > settings.alert_aqi_threshold, AirQualityMeasurement.city==city)
    result = await db.execute(alerts_city_by_city_query)
    alerts = result.scalars().all()
    
    return alerts