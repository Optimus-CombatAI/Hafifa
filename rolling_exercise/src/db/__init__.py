# Importing every table here registers them all on Base as soon as anything from src.db is used,
# so create_all sees them and the relationships between them can be resolved.
from src.db.air_quality_record import AirQualityRecord
from src.db.alert import Alert

__all__ = ["AirQualityRecord", "Alert"]
