from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.db.models import AirQualityMeasurement
from app.schemas.air_quality import AirQualityMeasurementOut
from app.db.session import get_db

router = APIRouter()

@router.get("/history", response_model=list[AirQualityMeasurementOut])
async def get_history( start_date: date, end_date: date,db: AsyncSession = Depends(get_db),) -> list[AirQualityMeasurementOut]:

    if start_date > end_date:
        raise HTTPException(status_code=400,detail="start_date must be before or equal to end_date",)

    stmt = select(AirQualityMeasurement).where(AirQualityMeasurement.date >= start_date, AirQualityMeasurement.date <= end_date, )
    result = await db.execute(stmt)
    measurements = result.scalars().all()

    return measurements

