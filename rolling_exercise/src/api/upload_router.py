from fastapi import APIRouter, UploadFile, status

from src.api.dependencies import UploadServiceDependency
from src.models.upload_report import UploadReport

router = APIRouter(prefix="/air-quality", tags=["air quality"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_air_quality_file(file: UploadFile, upload_service: UploadServiceDependency) -> UploadReport:
    return upload_service.upload(file.filename, file.file.read())
