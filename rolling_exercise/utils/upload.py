import typing
import sqlalchemy
import pandas as pd
import io
import fastapi
import pydantic

from rolling_exercise.utils.logging import air_quality_api_logger
from rolling_exercise.schemas.air_quality import AirQualityBase
from rolling_exercise.models.air_quality import AirQuality
from rolling_exercise.models.alert import Alert
from rolling_exercise.services.calculate_aqi import calculate_aqi

DEFAULT_ENCODING = 'utf-8'
HIGH_AQI_THRESHOLD = 300


def read_csv_file(file_contents: bytes, filename: str):
    try:
        df = pd.read_csv(io.StringIO(file_contents.decode(DEFAULT_ENCODING)))

        if df.empty or df.isnull().all().any():
            raise pd.errors.ParserError("CSV file is empty or contains only null values")

        return df
    except (pd.errors.ParserError, ValueError) as error:
        air_quality_api_logger.error(f"CSV file parsing error for {filename}: {str(error)}")

        raise fastapi.HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": f"The file {filename} could not be parsed. Check the file format."
            }
        )


def validate_records(df: pd.DataFrame, filename: str):
    df = df.where(pd.notna(df), None)
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
            error_message = f"{row}\n{str(error)}"
            validation_errors.append(error_message)
            air_quality_api_logger.error(f"Validation error for file: {filename}\n{error_message}")

    return records, validation_errors


async def process_csv(file: fastapi.UploadFile):
    try:
        air_quality_api_logger.info(f"Received file upload: {file.filename}")
        contents = await file.read()

        df = read_csv_file(contents, file.filename)
        records, validation_errors = validate_records(df, file.filename)

        if not records:
            air_quality_api_logger.error(f"No valid data found after processing file: {file.filename}.")

            raise fastapi.HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "No valid data found after processing the file."
                }
            )

        air_quality_api_logger.info(f"Successfully processed {len(records)} rows from {file.filename}")

        return records, validation_errors

    except fastapi.HTTPException as error:

        raise error

    except Exception as error:
        air_quality_api_logger.error(f"Unexpected error while processing file {file.filename}: {str(error)}")

        raise fastapi.HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "An unexpected error occurred while processing the file."
            }
        )


def create_db_records(records: typing.List[AirQualityBase]):
    db_records = []
    alert_records = []

    for record in records:
        aqi, aqi_level = calculate_aqi(record.pm2_5, record.no2, record.co2)

        air_quality_api_logger.info(
            f"Calculated AQI for City: {record.city}, Date: {record.date} - "
            f"PM2.5: {record.pm2_5}, NO2: {record.no2}, CO2: {record.co2}, "
            f"AQI: {aqi}, AQI Level: {aqi_level}"
        )

        db_records.append(AirQuality(
            date=record.date,
            city=record.city,
            pm2_5=record.pm2_5,
            no2=record.no2,
            co2=record.co2,
            aqi=aqi,
            aqi_level=aqi_level,
        ))

        if aqi > HIGH_AQI_THRESHOLD:
            alert_records.append(Alert(
                date=record.date,
                city=record.city,
                aqi=aqi,
                aqi_level=aqi_level
            ))
            air_quality_api_logger.warning(
                f"High AQI Alert - City: {record.city}, Date: {record.date}, AQI: {aqi}"
            )

    return db_records, alert_records


def save_records_to_db(
        db_session: sqlalchemy.orm.Session,
        db_records: typing.List[AirQuality],
        alert_records: typing.List[Alert]
):
    try:
        db_session.bulk_save_objects(db_records)

        if alert_records:
            db_session.bulk_save_objects(alert_records)

        db_session.commit()
        air_quality_api_logger.info(f"Successfully added {len(db_records)} records to the database.")

        if alert_records:
            air_quality_api_logger.info(f"Created {len(alert_records)} high AQI alerts.")

    except Exception as error:
        db_session.rollback()
        air_quality_api_logger.error(f"Error while saving records to the database: {str(error)}")

        raise fastapi.HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to save records to the database."
            }
        )


async def add_records_to_db(
        records: typing.List[AirQualityBase],
        db_session: sqlalchemy.orm.Session
):
    db_records, alert_records = create_db_records(records)
    save_records_to_db(db_session, db_records, alert_records)
