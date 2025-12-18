
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI

from db.database import db
from routers.air_quality_router import router as air_quality_router
from routers.aqi_statistics_router import router as aqi_statistics_router
from routers.alerts_router import router as alerts_router
from logger import LoggerConfig
from settings import settings
import connectors.db_connector as db_connector


@asynccontextmanager
async def lifespan(app: FastAPI):
    # -------- startup --------
    LoggerConfig()

    await db.reset_tables(drop_previous=settings.DELETE_PREV_TABLES)
    await db.create_tables()
    await db_connector.fill_dummy_data(
        use_dummy_dataset=settings.USE_DUMMY_DATASET
    )

    yield

    # -------- shutdown --------
    # (put cleanup here if needed)
    # e.g. await db.close()


app = FastAPI(lifespan=lifespan)


app.include_router(air_quality_router)
app.include_router(aqi_statistics_router)
app.include_router(alerts_router)


if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8000)