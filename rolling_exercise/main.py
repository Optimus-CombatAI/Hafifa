from fastapi import FastAPI

from db.db_functions import set_up_db, fill_dummy_data
from routers.air_quality_router import router as air_quality_router
from routers.aqi_router import router as aqi_router
from routers.alerts_router import router as alerts_router


set_up_db()
fill_dummy_data()

app = FastAPI()


app.include_router(air_quality_router)
app.include_router(aqi_router)
app.include_router(alerts_router)
