import sqlalchemy
import fastapi
import datetime as dt

from ..models.alert import Alert
from ..utils.logging import air_quality_api_logger


def get_all_alerts(db: sqlalchemy.orm.Session):
    try:
        air_quality_api_logger.info("Fetching all alerts.")
        alerts = db.query(Alert).all()

        if not alerts:
            air_quality_api_logger.warning("No alerts found.")
            raise fastapi.HTTPException(
                status_code=404,
                detail={"status": "error", "message": "No alerts found."},
            )

        return alerts

    except Exception as error:
        air_quality_api_logger.error(f"Error fetching alerts: {str(error)}")
        raise fastapi.HTTPException(
            status_code=500,
            detail={"status": "error", "message": "Failed to fetch alerts."},
        )


def get_alerts_by_date(date: dt.date, db: sqlalchemy.orm.Session):
    try:
        air_quality_api_logger.info(f"Fetching alerts for date: {date}.")
        alerts = db.query(Alert).filter(Alert.date == date).all()

        if not alerts:
            air_quality_api_logger.warning(f"No alerts found for date {date}.")
            raise fastapi.HTTPException(
                status_code=404,
                detail={"status": "error", "message": f"No alerts found for date {date}."},
            )

        return alerts

    except Exception as error:
        air_quality_api_logger.error(f"Error fetching alerts for date {date}: {str(error)}")
        raise fastapi.HTTPException(
            status_code=500,
            detail={"status": "error", "message": f"Failed to fetch alerts for date {date}."},
        )


def get_alerts_by_city(city: str, db: sqlalchemy.orm.Session):
    try:
        air_quality_api_logger.info(f"Fetching alerts for city: {city}.")
        alerts = db.query(Alert).filter(Alert.city == city).all()

        if not alerts:
            air_quality_api_logger.warning(f"No alerts found for city {city}.")
            raise fastapi.HTTPException(
                status_code=404,
                detail={"status": "error", "message": f"No alerts found for city {city}."},
            )

        return alerts

    except Exception as error:
        air_quality_api_logger.error(f"Error fetching alerts for city {city}: {str(error)}")
        raise fastapi.HTTPException(
            status_code=500,
            detail={"status": "error", "message": f"Failed to fetch alerts for city {city}."},
        )