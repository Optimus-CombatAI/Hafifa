from fastapi import FastAPI
from consts import LOGGER
from routers.air_quality_router import router as air_quality_router
from routers.aqi_router import router as aqi_router
from routers.alerts_router import router as alerts_router

app = FastAPI()


app.include_router(air_quality_router)
app.include_router(aqi_router)
app.include_router(alerts_router)
