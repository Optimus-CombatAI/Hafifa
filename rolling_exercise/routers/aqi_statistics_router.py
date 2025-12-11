from fastapi import APIRouter

router = APIRouter(
    prefix="/aqi_statistics",
    tags=["AQI Statistics"]
)


@router.get("/history")
async def get_aqi_history_by_city(city_name: str):
    """
    This function return the aqi history of a given city
    :param city_name: the name of the city to get history of aqi
    :return: aqi history of the given city
    """

    return {"aqi": "?"}


@router.get("/average")
def get_avg_aqi_by_city(city_name: str):
    """
    This function returns the average aqi score for a given city
    :param city_name: the name of the city to calculate the average aqi
    :return: the average aqi score
    """

    return {"aqi": "?"}


@router.get("/best_cities")
def get_aqi_best_cities():
    """
    This function returns 3 cities with the best aqi score(the lowest score)
    :return: 3 cities with lowest aqi
    """

    return {"aqi": "?"}
