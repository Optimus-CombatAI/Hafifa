import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AirQualityMeasurement
from app.services.aqi_service import calculate_aqi_data
from app.services.csv_service import parse_air_quality_csv
from app.core.logger import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

async def ingest_air_quality_csv(*, file_content: bytes, db: AsyncSession) -> int:
    logger.info("Starting CSV ingestion...")

    rows = parse_air_quality_csv(file_content)
    logger.info(f"CSV parsed successfully. {len(rows)} rows found.")

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
        logger.info(f"CSV ingestion completed. {len(rows)} rows inserted.")
        return len(rows)

    except SQLAlchemyError as exc:
        logger.error(f"Database error during ingest: {exc}")
        await db.rollback()
        raise
