import sqlalchemy
import fastapi
import datetime as dt

from sqlalchemy.exc import NoResultFound

from rolling_exercise.models.air_quality import AirQuality
from rolling_exercise.utils.logging import air_quality_api_logger


def get_air_quality_by_date_range(
        start_date: dt.date,
        end_date: dt.date,
        db: sqlalchemy.orm.Session,
):
    try:
        air_quality_api_logger.info(f"Fetching air quality data from {start_date} to {end_date}.")

        if start_date > end_date:
            raise fastapi.HTTPException(
                status_code=422,
                detail={"status": "error", "message": "Start date cannot be after end date"}
            )

        if not isinstance(start_date, dt.date) or not isinstance(end_date, dt.date):
            raise fastapi.HTTPException(
                status_code=422,
                detail={"status": "error", "message": "Invalid date format"}
            )

        records = (
            db.query(AirQuality)
            .filter(AirQuality.date >= start_date, AirQuality.date <= end_date)
            .all()
        )

        if not records:
            air_quality_api_logger.warning(
                f"No air quality data found for the range {start_date} to {end_date}."
            )
            raise fastapi.HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "message": f"No air quality data found in range {start_date} to {end_date}."
                }
            )

        air_quality_api_logger.info(
            f"Successfully fetched {len(records)} air quality records from {start_date} to {end_date}."
        )

        return records

    except fastapi.HTTPException as http_error:
        air_quality_api_logger.error(f"HTTPException occurred: {http_error.status_code} - {http_error.detail}")

        raise http_error

    except Exception as error:
        air_quality_api_logger.error(f"Error fetching air quality data: {str(error)}")

        raise fastapi.HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to fetch air quality data."
            }
        )


def get_air_quality_by_city(city: str, db: sqlalchemy.orm.Session):
    try:
        air_quality_api_logger.info(f"Fetching air quality data for city: {city}.")
        records = db.query(AirQuality).filter(AirQuality.city == city).all()

        if not records:
            air_quality_api_logger.warning(f"No air quality data found for city {city}.")
            raise fastapi.HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "message": f"No air quality data found for city {city}."
                }
            )

        air_quality_api_logger.info(f"Successfully fetched {len(records)} air quality records for city {city}.")
        return records
    except fastapi.HTTPException as http_error:
        raise http_error
    except Exception as error:
        air_quality_api_logger.error(f"Error fetching air quality data for city {city}: {str(error)}")
        raise fastapi.HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"Failed to fetch air quality data for city {city}."
            }
        )


def get_city_aqi_history(city: str, db: sqlalchemy.orm.Session):
    try:
        air_quality_api_logger.info(f"Fetching AQI history for city: {city}.")
        records = (
            db.query(AirQuality.date, AirQuality.aqi, AirQuality.aqi_level)
            .filter(AirQuality.city == city)
            .order_by(AirQuality.date)
            .all()
        )

        if not records:
            air_quality_api_logger.warning(f"No AQI history found for city {city}.")
            raise fastapi.HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "message": f"No AQI history found for city {city}."
                }
            )

        air_quality_api_logger.info(f"Successfully fetched AQI history for city {city}.")
        return {
            "data": {
                "city": city,
                "history": [{
                    "date": record.date, "aqi": record.aqi, "aqi_level": record.aqi_level} for record in records
                ]
            }
        }
    except fastapi.HTTPException as http_error:
        raise http_error
    except Exception as error:
        air_quality_api_logger.error(f"Error fetching AQI history for city {city}: {str(error)}")
        raise fastapi.HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"Failed to fetch AQI history for city {city}."
            }
        )


def get_city_aqi_average(city: str, db: sqlalchemy.orm.Session):
    try:
        air_quality_api_logger.info(f"Fetching AQI average for city: {city}.")
        avg_aqi = (
            db.query(sqlalchemy.func.avg(AirQuality.aqi))
            .filter(AirQuality.city == city)
            .one()
        )

        air_quality_api_logger.info(f"Successfully fetched AQI average for city {city}: {avg_aqi[0]}.")
        return {"data": {"city": city, "average_aqi": avg_aqi[0]}}

    except NoResultFound:
        air_quality_api_logger.warning(f"No AQI data found for city {city}.")
        raise fastapi.HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": f"No AQI data found for city {city}."
            }
        )
    except fastapi.HTTPException as http_error:
        raise http_error
    except Exception as error:
        air_quality_api_logger.error(f"Error fetching AQI average for city {city}: {str(error)}")
        raise fastapi.HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"Failed to fetch AQI average for city {city}."
            }
        )


def get_best_cities(db: sqlalchemy.orm.Session):
    try:
        air_quality_api_logger.info("Fetching the best cities based on AQI.")
        cities = (
            db.query(AirQuality.city, sqlalchemy.func.avg(AirQuality.aqi).label("average_aqi"))
            .group_by(AirQuality.city)
            .order_by(sqlalchemy.asc("average_aqi"))
            .limit(3)
            .all()
        )

        if not cities:
            air_quality_api_logger.warning("No cities found with AQI data.")
            raise fastapi.HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "message": "No cities found with AQI data."
                }
            )

        air_quality_api_logger.info(f"Successfully fetched the top 3 cities based on AQI.")
        return {
            "data": {
                "best_cities": [{"city": city.city, "average_aqi": city.average_aqi} for city in cities]
            }
        }
    except fastapi.HTTPException as http_error:
        raise http_error
    except Exception as error:
        air_quality_api_logger.error(f"Error fetching best cities: {str(error)}")
        raise fastapi.HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to fetch best cities."
            }
        )
