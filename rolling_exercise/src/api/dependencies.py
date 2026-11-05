from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from src.parsing.air_quality_csv_parser import AirQualityCsvParser
from src.repositories.air_quality_repository import AirQualityRepository
from src.services.air_quality_upload_service import AirQualityUploadService
from src.services.aqi_calculator import AqiCalculator


def get_session(request: Request) -> Iterator[Session]:
    """One session per request, closed when the response is sent."""
    with request.app.state.session_factory() as session:
        yield session


SessionDependency = Annotated[Session, Depends(get_session)]


def get_air_quality_repository(session: SessionDependency) -> AirQualityRepository:
    return AirQualityRepository(session)


AirQualityRepositoryDependency = Annotated[AirQualityRepository, Depends(get_air_quality_repository)]


def get_upload_service(
    request: Request, air_quality_repository: AirQualityRepositoryDependency
) -> AirQualityUploadService:
    return AirQualityUploadService(
        AirQualityCsvParser(), AqiCalculator(), air_quality_repository, request.app.state.settings.alert_aqi_threshold
    )


UploadServiceDependency = Annotated[AirQualityUploadService, Depends(get_upload_service)]
