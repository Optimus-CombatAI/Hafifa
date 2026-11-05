import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.errors import CityNotFoundError, InvalidCsvFileError

logger = logging.getLogger(__name__)


def handle_invalid_csv_file(request: Request, error: InvalidCsvFileError) -> JSONResponse:
    logger.warning(f"Rejected upload to {request.url.path}: {error}")

    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(error)})


def handle_city_not_found(request: Request, error: CityNotFoundError) -> JSONResponse:
    logger.info(f"{request.url.path}: {error}")

    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(error)})
