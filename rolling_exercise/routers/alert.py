import fastapi
import sqlalchemy
import datetime as dt
import typing

from rolling_exercise.database.session import get_db
from rolling_exercise.schemas.alert import AlertResponse
from rolling_exercise.crud.alert import (
    get_all_alerts,
    get_alerts_by_date,
    get_alerts_by_city,
)

alerts_router = fastapi.APIRouter(prefix="/alerts", tags=["alerts"])


@alerts_router.get("/", response_model=typing.List[AlertResponse])
async def get_all_alerts(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    try:
        alerts = get_all_alerts(db)

        return alerts

    except fastapi.HTTPException as error:
        raise error


@alerts_router.get("/date", response_model=typing.List[AlertResponse])
async def get_alerts_by_date(date: dt.date, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    try:
        alerts = get_alerts_by_date(date, db)

        return alerts

    except fastapi.HTTPException as error:
        raise error


@alerts_router.get("/city", response_model=typing.List[AlertResponse])
async def get_alerts_by_city(city: str, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    try:
        alerts = get_alerts_by_city(city, db)

        return alerts

    except fastapi.HTTPException as error:
        raise error
