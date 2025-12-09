import asyncio
from fastapi import FastAPI

from db.db_functions import set_up_db, fill_dummy_data, close_session
from routers.air_quality_router import router as air_quality_router
from routers.aqi_router import router as aqi_router
from routers.alerts_router import router as alerts_router


app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await set_up_db()
    await fill_dummy_data()


@app.on_event("shutdown")
def on_shutdown():
    close_session()


app.include_router(air_quality_router)
app.include_router(aqi_router)
app.include_router(alerts_router)
