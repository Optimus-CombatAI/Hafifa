import pandas as pd
import os
from datetime import datetime
from typing import List
from .logging import app_logger

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    required_columns = ["city", "date", "PM2.5", "NO2", "CO2"]

    for column in required_columns:
        if column not in df.columns:
            app_logger.error(f"Missing required column: {column}")
            raise ValueError(f"Missing required column: {column}")

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    invalid_dates = df[df['date'].isnull()]
    if not invalid_dates.empty:
        app_logger.error(f"Invalid date formats found in rows: {invalid_dates}")
        raise ValueError(f"Invalid date format found for some rows: {invalid_dates}")  # Raise error for invalid dates

    df['PM2.5'] = pd.to_numeric(df['PM2.5'], errors='coerce')
    df['NO2'] = pd.to_numeric(df['NO2'], errors='coerce')
    df['CO2'] = pd.to_numeric(df['CO2'], errors='coerce')

    invalid_rows = df[df[['PM2.5', 'NO2', 'CO2']].isnull().any(axis=1)]
    if not invalid_rows.empty:
        app_logger.error(f"Invalid pollutant values found in rows: {invalid_rows}")
        raise ValueError(f"Missing or invalid pollutant values for rows: {invalid_rows}")  # Raise error for invalid pollutants

    return df


def process_csv(file: UploadFile) -> pd.DataFrame:
    """
    Process the uploaded CSV file (from an UploadFile object) with pandas.
    """
    try:
        # Read the file's content
        contents = await file.read()
        # Convert the content to a pandas DataFrame (assuming the file is CSV)
        df = pd.read_csv(StringIO(contents.decode('utf-8')))

        # Validate the data
        validated_df = validate_data(df)

        if validated_df.empty:
            logger.error("No valid data in the file.")
            raise ValueError("No valid data found after validation.")  # Raise error if no valid data

        logger.info(f"Successfully processed {len(validated_df)} rows.")
        return validated_df

    except pd.errors.ParserError as e:
        logger.error(f"CSV file parsing error: {str(e)}")
        raise ValueError("The file could not be parsed. Please check the file format.")  # Handle invalid CSV format
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        raise ValueError(f"Data validation error: {str(e)}")  # Catch validation errors
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise RuntimeError("An unexpected error occurred while processing the file.")  # Handle other unexpected errors
