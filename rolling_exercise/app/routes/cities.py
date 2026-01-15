from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.schemas.air_quality import AirQualityMeasurementOut, CityAqiAverageOut
from app.db.models import AirQualityMeasurement

router = APIRouter()

@router.get("/cities/best", response_model=list[CityAqiAverageOut])
async def get_best_cities(db: AsyncSession = Depends(get_db)) -> list[CityAqiAverageOut]:
    average_aqi = func.avg(AirQualityMeasurement.aqi).label("average_aqi")
    stmt = (select(AirQualityMeasurement.city, average_aqi).group_by(AirQualityMeasurement.city).order_by(average_aqi.asc()).limit(3))
    result = await db.execute(stmt)
    rows = result.all()

    if not rows:
        return []

    return [{"city": city, "average_aqi": avg} for city, avg in rows]

@router.get("/cities/{city}", response_model=list[AirQualityMeasurementOut])
async def get_city_measurements(city:str ,db: AsyncSession = Depends(get_db)):
    city_query = select(AirQualityMeasurement).where(AirQualityMeasurement.city == city)
    result = await db.execute(city_query)
    measurements = result.scalars().all()
    if not measurements:
        raise HTTPException(status_code=404,detail= "unknown city") 

    return measurements

@router.get("/cities/{city}/average",response_model=CityAqiAverageOut)
async def get_average_city_aqi(city:str, db:AsyncSession = Depends(get_db)):
    average_query = select(func.avg(AirQualityMeasurement.aqi)).where(AirQualityMeasurement.city==city)
    result = await db.execute(average_query)
    average_aqi = result.scalar()
    if average_aqi is None:
        raise HTTPException(status_code=404,detail="no measurements found for this city")
    
    return {"city":city,"average_aqi":average_aqi}