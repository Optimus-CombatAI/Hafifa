from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.air_quality import AirQualityMeasurementOut
from app.services.alerts_service import fetch_alerts, fetch_alerts_by_city

router = APIRouter(prefix="/alerts")


@router.get("", response_model=list[AirQualityMeasurementOut])
async def get_alerts(session: AsyncSession = Depends(get_db)) -> list[AirQualityMeasurementOut]:
    return await fetch_alerts(session=session)


@router.get("/city/{city}", response_model=list[AirQualityMeasurementOut])
async def get_alerts_by_city(city: str, session: AsyncSession = Depends(get_db),) -> list[AirQualityMeasurementOut]:
    return await fetch_alerts_by_city(session=session, city=city)
