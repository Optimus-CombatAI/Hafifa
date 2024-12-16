import fastapi
import sqlalchemy
import datetime as dt
import typing

from rolling_exercise.database.session import get_db
from rolling_exercise.schemas.air_quality import AirQualityResponse
from rolling_exercise.crud.air_quality import (
    get_air_quality_by_date_range,
    get_air_quality_by_city,
    get_city_aqi_history,
    get_city_aqi_average,
    get_best_cities,
)

from rolling_exercise.utils.upload import process_csv, add_records_to_db

air_quality_router = fastapi.APIRouter(prefix="/air-quality", tags=["air-quality"])


@air_quality_router.post("/upload-air-quality-csv")
async def upload_air_quality_csv(
    file: fastapi.UploadFile = fastapi.File(...),
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db)
):
    try:
        records, validation_errors = await process_csv(file)
        await add_records_to_db(records, db)

        return {
            "status": "success",
            "message": f"Successfully uploaded {len(records)} air quality records",
            "validation errors": validation_errors
        }

    except fastapi.HTTPException as error:
        raise error


@air_quality_router.get("/records", response_model=typing.List[AirQualityResponse])
async def get_air_quality_data(
    start_date: dt.date,
    end_date: dt.date,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db)
):
    try:
        records = get_air_quality_by_date_range(start_date, end_date, db)

        return records

    except fastapi.HTTPException as error:
        raise error


@air_quality_router.get("/city/{city}", response_model=typing.List[AirQualityResponse])
async def get_air_quality_by_city_route(
    city: str,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db)
):
    try:
        records = get_air_quality_by_city(city, db)

        return records

    except fastapi.HTTPException as error:
        raise error


@air_quality_router.get("/city/{city}/aqi/history", response_model=typing.Dict)
async def get_city_aqi_history_route(
    city: str,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db)
):
    try:
        history = get_city_aqi_history(city, db)

        return history

    except fastapi.HTTPException as error:
        raise error


@air_quality_router.get("/city/{city}/aqi/average", response_model=typing.Dict)
async def get_city_aqi_average_route(
    city: str,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db)
):
    try:
        average = get_city_aqi_average(city, db)

        return average

    except fastapi.HTTPException as error:
        raise error


@air_quality_router.get("/best-cities", response_model=typing.Dict)
async def get_best_cities_route(
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db)
):
    try:
        best_cities = get_best_cities(db)

        return best_cities

    except fastapi.HTTPException as error:
        raise error
