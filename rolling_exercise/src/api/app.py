from fastapi import FastAPI

from src.api import air_quality_router, health_router, upload_router
from src.api.exception_handlers import handle_city_not_found, handle_invalid_csv_file
from src.configs.settings import ApiSettings
from src.db.database import create_session_factory
from src.errors import CityNotFoundError, InvalidCsvFileError


def create_app(settings: ApiSettings) -> FastAPI:
    app = FastAPI(title="Air Quality API")
    app.state.settings = settings
    app.state.session_factory = create_session_factory(settings.database_url)

    app.include_router(health_router.router)
    app.include_router(upload_router.router)
    app.include_router(air_quality_router.router)
    app.add_exception_handler(InvalidCsvFileError, handle_invalid_csv_file)
    app.add_exception_handler(CityNotFoundError, handle_city_not_found)

    return app
