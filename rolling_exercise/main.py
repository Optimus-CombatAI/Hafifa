import fastapi
import sqlalchemy

from rolling_exercise.routers.air_quality import air_quality_router
from rolling_exercise.routers.alert import alerts_router
from rolling_exercise.utils.logging import air_quality_api_logger
from rolling_exercise.database.session import engine

app = fastapi.FastAPI()

sqlalchemy.orm.declarative_base().metadata.create_all(bind=engine)

app.include_router(air_quality_router)
app.include_router(alerts_router)


@app.on_event("startup")
async def startup():
    air_quality_api_logger.info("Air Quality API started")


@app.on_event("shutdown")
async def shutdown():
    air_quality_api_logger.info("Air Quality API stopped")
