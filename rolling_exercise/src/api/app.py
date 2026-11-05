from fastapi import FastAPI

from src.api import health_router, upload_router
from src.api.exception_handlers import handle_invalid_csv_file
from src.configs.settings import ApiSettings
from src.db.database import create_session_factory
from src.errors import InvalidCsvFileError


def create_app(settings: ApiSettings) -> FastAPI:
    app = FastAPI(title="Air Quality API")
    app.state.settings = settings
    app.state.session_factory = create_session_factory(settings.database_url)

    app.include_router(health_router.router)
    app.include_router(upload_router.router)
    app.add_exception_handler(InvalidCsvFileError, handle_invalid_csv_file)

    return app
