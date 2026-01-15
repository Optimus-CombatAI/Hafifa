from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import get_db
from app.db.models import AirQualityMeasurement
from app.services.csv_service import parse_air_quality_csv
from app.services.aqi_service import calculate_aqi_data

router = APIRouter()


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...),db: AsyncSession = Depends(get_db),) -> Response:
    content = await file.read()

    try:
        rows = parse_air_quality_csv(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        for row in rows:
            aqi_data = calculate_aqi_data(row.pm25, row.no2, row.co2)

            measurement = AirQualityMeasurement(
                date=row.date,
                city=row.city,
                pm25=row.pm25,
                no2=row.no2,
                co2=row.co2,
                aqi=aqi_data.aqi,
                aqi_level=aqi_data.aqi_level,
            )
            db.add(measurement)

        await db.commit()

    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error") from exc

    return Response(content="ok", media_type="text/plain")
