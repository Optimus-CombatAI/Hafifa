from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AirQualityMeasurement
import logging
from app.core.logger import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

async def fetch_best_cities(*, session: AsyncSession, limit: int) -> list[tuple[str, float]]:
    logger.info(f"Fetching best cities (limit={limit})")

    average_aqi = func.avg(AirQualityMeasurement.aqi).label("average_aqi")
    stmt = (
        select(AirQualityMeasurement.city, average_aqi)
        .group_by(AirQualityMeasurement.city)
        .order_by(average_aqi.asc(), AirQualityMeasurement.city.asc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    rows = result.all()
    logger.info(f"Best cities fetched:{len(rows)} results")
    return rows

async def fetch_by_city(*, session: AsyncSession, city: str) -> list[AirQualityMeasurement]:
    logger.info(f"Fetching measurements for city={city}")

    stmt = select(AirQualityMeasurement).where(AirQualityMeasurement.city == city)
    result = await session.execute(stmt)
    rows = result.scalars().all()

    if not rows:
        raise KeyError(city)

    logger.info(f"City={city}: {len(rows)} rows")
    return rows

async def fetch_average_city_aqi(*, city: str, session: AsyncSession) -> float:
    logger.info(f"Computing average AQI for city={city}")

    stmt = select(func.avg(AirQualityMeasurement.aqi)).where(AirQualityMeasurement.city == city)
    result = await session.execute(stmt)
    avg = result.scalar()

    if avg is None:
        raise KeyError(city)

    return avg
