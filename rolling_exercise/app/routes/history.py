from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.air_quality import AirQualityMeasurementOut
from app.services.history_service import fetch_history

router = APIRouter()


@router.get("/history", response_model=list[AirQualityMeasurementOut])
async def get_history(start_date: date,end_date: date,db: AsyncSession = Depends(get_db),) -> list[AirQualityMeasurementOut]:
    if start_date > end_date:
        
        raise HTTPException(status_code=400, detail="start_date must be <= end_date")

    return await fetch_history(db=db, start_date=start_date, end_date=end_date)
