import fastapi
import sqlalchemy
from .routers.air_quality import air_quality_router
from .routers.alert import alert_router
from .utils.logging import air_quality_api_logger

from database.session import engine

app = fastapi.FastAPI()

sqlalchemy.orm.Base.metadata.create_all(bind=engine)

app.include_router(air_quality_router)
app.include_router(alert_router)


@app.on_event("startup")
async def startup():
    air_quality_api_logger.info("Air Quality API started")


@app.on_event("shutdown")
async def shutdown():
    air_quality_api_logger.info("Air Quality API stopped")
