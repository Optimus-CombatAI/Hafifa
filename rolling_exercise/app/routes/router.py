from fastapi import APIRouter

from app.routes.upload import router as upload_router
from app.routes.cities import router as cities_router
from app.routes.alerts import router as alerts_router
from app.routes.history import router as history_router

api_router = APIRouter()

api_router.include_router(upload_router, tags=["upload"])
api_router.include_router(cities_router,tags=["cities"])
api_router.include_router(alerts_router,tags=["alerts"])
api_router.include_router(history_router,tags=["history"])