
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn


from db.database import Database
from exceptions.connectionException import ConnectionException
from routers.air_quality_router import AirQualityRouter
from routers.aqi_statistics_router import AQIStatisticsRouter
from routers.alerts_router import AlertsRouter
from logger import LoggerConfig
from settings import settings
import tests.db_connector as db_connector


async def _on_startup(app_db) -> None:
    LoggerConfig()

    await app_db.reset_tables(drop_previous=settings.DELETE_PREV_TABLES)
    await app_db.create_tables()
    await db_connector.fill_dummy_data(
        use_dummy_dataset=settings.USE_DUMMY_DATASET
    )


def create_lifespan(app_db: Database):
    @asynccontextmanager
    async def lifespan(fast_api_app: FastAPI):
        await _on_startup(app_db)
        yield

    return lifespan


def create_app(app_db: Database) -> FastAPI:
    fast_api_app = FastAPI(lifespan=create_lifespan(app_db))

    @fast_api_app.exception_handler(ConnectionException)
    async def connection_exception_handler(request: Request, exc: ConnectionException, ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={"detail": exc.message},
        )

    fast_api_app.include_router(AirQualityRouter(app_db))
    fast_api_app.include_router(AQIStatisticsRouter(app_db))
    fast_api_app.include_router(AlertsRouter(app_db))

    return fast_api_app


if __name__ == '__main__':
    db = Database(settings.DB_URL, settings.MOCK_SCHEME)
    app = create_app(db)
    uvicorn.run(app, host='127.0.0.1', port=8000)
