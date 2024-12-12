import sqlalchemy.orm
import pandas as pd
import io
import fastapi
import pydantic
from .logging import air_quality_api_logger
from ..schemas.air_quality import AirQualityBase
from ..models.air_quality import AirQuality
import sqlalchemy
from ..services.calculate_aqi import calculate_aqi


async def process_csv(file: fastapi.UploadFile):
    try:
        air_quality_api_logger.info(f"Received file upload: {file.filename}")

        contents = await file.read()
        try:
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        except pd.errors.ParserError as error:
            air_quality_api_logger.error(
                f"CSV file parsing error for {file.filename}: {str(error)}")
            raise fastapi.HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": f"The file '{file.filename}' could not be parsed. Check the file format."
                }
            )

        records = []
        validation_errors = []

        for _, row in df.iterrows():
            try:
                record = AirQualityBase(
                    date=row['date'],
                    city=row['city'],
                    pm2_5=row['PM2.5'],
                    no2=row['NO2'],
                    co2=row['CO2'],
                )
                records.append(record)

            except pydantic.ValidationError as error:
                error_message = f"row {row}: {str(error)}"
                validation_errors.append(error_message)
                air_quality_api_logger.error(
                    f"Validation error for file: {file.filename} for {error_message}"
                )

                continue

        if not records:
            air_quality_api_logger.error(
                f"No valid data found after processing file: {file.filename}.")
            raise fastapi.HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "No valid data found after processing the file."
                }
            )

        air_quality_api_logger.info(
            f"Successfully processed {len(records)} rows from {file.filename}"
        )

        return {"data": records, "validation_errors": validation_errors}

    except fastapi.HTTPException as error:
        raise error
    except Exception as error:
        air_quality_api_logger.error(
            f"Unexpected error while processing file {file.filename}: {str(error)}"
        )
        raise fastapi.HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "An unexpected error occurred while processing the file."
            }
        )


def add_records_to_db(records: list, db_session: sqlalchemy.orm.Session):
    try:
        air_quality_api_logger.info(f"Attempting to add {len(records)} records to the database.")

        db_records = []

        for record in records:
            aqi, aqi_level = calculate_aqi(record.pm2_5, record.no2, record.co2)

            air_quality_api_logger.info(
                f"Calculated AQI for City: {record.city}, Date: {record.date} - "
                f"PM2.5: {record.pm2_5}, NO2: {record.no2}, CO2: {record.co2}, "
                f"AQI: {aqi}, AQI Level: {aqi_level}"
            )

            db_record = AirQuality(
                date=record.date,
                city=record.city,
                pm2_5=record.pm2_5,
                no2=record.no2,
                co2=record.co2,
                aqi=aqi,
                aqi_level=aqi_level,
            )
            db_records.append(db_record)

        db_session.bulk_save_objects(db_records)
        db_session.commit()

        air_quality_api_logger.info(
            f"Successfully added {len(db_records)} records to the database."
        )

        return {"data": {"message": f"Successfully added {len(db_records)} records to the database."}}

    except Exception as error:
        db_session.rollback()
        air_quality_api_logger.error(
            f"Error while adding {len(records)} records to the database: {str(error)}"
        )
        raise fastapi.HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to add records to the database."
            }
        )
