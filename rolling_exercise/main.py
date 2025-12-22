
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn


from db.database import db
from exceptions.connectionException import ConnectionException
from routers.air_quality_router import router as air_quality_router
from routers.aqi_statistics_router import router as aqi_statistics_router
from routers.alerts_router import router as alerts_router
from logger import LoggerConfig
from settings import settings
import tests.db_connector as db_connector


async def _on_startup() -> None:
    LoggerConfig()

    await db.reset_tables(drop_previous=settings.DELETE_PREV_TABLES)
    await db.create_tables()
    await db_connector.fill_dummy_data(
        use_dummy_dataset=settings.USE_DUMMY_DATASET
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _on_startup()

    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(ConnectionException)
async def connection_exception_handler(request: Request, exc: ConnectionException,) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": exc.message},
    )


app.include_router(air_quality_router)
app.include_router(aqi_statistics_router)
app.include_router(alerts_router)


if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8000)
