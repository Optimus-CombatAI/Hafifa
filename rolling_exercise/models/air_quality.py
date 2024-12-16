import sqlalchemy

from rolling_exercise.database.session import Base


class AirQuality(Base):
    __tablename__ = 'air_quality'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    city = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    pm2_5 = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    no2 = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    co2 = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    aqi = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    aqi_level = sqlalchemy.Column(sqlalchemy.String, nullable=False)
