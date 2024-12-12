import fastapi
import sqlalchemy

from ..database.session import get_db
from ..schemas.air_quality import AirQualityResponse
from ..utils.upload import process_csv, add_records_to_db
import starlette.status

air_quality_router = fastapi.APIRouter(prefix="/air_quality", tags=["air_quality"])


@air_quality_router.post("/upload-csv", response_model=AirQualityResponse)
async def upload_air_quality_csv(
    file: fastapi.UploadFile = fastapi.File(...),
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db)
):

    try:
        records, validation_errors = await process_csv(file)
        await add_records_to_db(records, db)

        return {
            "status": "success",
            "message": f"Successfully uploaded {len(records)} air quality records",
            "validation errors": validation_errors
        }

    except ValueError as e:
        raise fastapi.HTTPException(
            status_code=starlette.status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": str(e),
            }
        )

    except RuntimeError as e:
        raise fastapi.HTTPException(
            status_code=starlette.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": str(e),
            }
        )

