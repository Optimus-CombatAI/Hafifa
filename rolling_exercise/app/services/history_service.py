from __future__ import annotations
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AirQualityMeasurement
import logging
from app.core.logger import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

async def fetch_history(*, db: AsyncSession,start_date: date,end_date: date) -> list[AirQualityMeasurement]:
    stmt = select(AirQualityMeasurement).where(AirQualityMeasurement.date >= start_date,AirQualityMeasurement.date <= end_date,)
    logger.info(f"Fetching history: {start_date} → {end_date}")
    result = await db.execute(stmt)
    rows = result.scalars().all()
    logger.info(f"History results: {len(rows)} rows")

    return rows
