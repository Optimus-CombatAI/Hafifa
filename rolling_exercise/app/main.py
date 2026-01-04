
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn


from db.pgDatabase import PGDatabase
from exceptions.connectionException import ConnectionException
from routers.air_quality_router import AirQualityRouter
from routers.aqi_statistics_router import AQIStatisticsRouter
from routers.alerts_router import AlertsRouter
from logger import LoggerConfig
from settings import settings


async def _on_startup(app_db: PGDatabase) -> None:
    LoggerConfig()
    await app_db.create_tables()


def create_lifespan(app_db: PGDatabase):
    @asynccontextmanager
    async def lifespan(fast_api_app: FastAPI):
        await _on_startup(app_db)
        yield

    return lifespan


def create_app(app_db: PGDatabase) -> FastAPI:
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
    db = PGDatabase(settings.DB_URL, settings.SCHEME)
    app = create_app(db)
    uvicorn.run(app, host='127.0.0.1', port=8000)
