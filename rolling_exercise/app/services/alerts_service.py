from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.config import settings
from app.db.models import AirQualityMeasurement
import logging
from app.core.logger import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

async def fetch_alerts(*, session: AsyncSession) -> list[AirQualityMeasurement]:
    logger.info(f"Fetching alerts (threshold={settings.alert_aqi_threshold})")
    stmt = select(AirQualityMeasurement).where(AirQualityMeasurement.aqi > settings.alert_aqi_threshold)
    result = await session.execute(stmt)
    rows = result.scalars().all()
    logger.info(f"Alerts fetched: {len(rows)} rows")

    return rows


async def fetch_alerts_by_city(*, session: AsyncSession, city: str) -> list[AirQualityMeasurement]:
    logger.info(f"Fetching alerts for city={city}")
    stmt = select(AirQualityMeasurement).where(AirQualityMeasurement.aqi > settings.alert_aqi_threshold,AirQualityMeasurement.city == city,)
    result = await session.execute(stmt)
    rows = result.scalars().all()
    logger.info(f"Alerts for city={city}:{len(rows)} rows")
    
    return rows
