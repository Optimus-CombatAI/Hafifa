import sqlalchemy

from rolling_exercise.database.session import Base


class Alert(Base):
    __tablename__ = 'alerts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    city = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    aqi = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    aqi_level = sqlalchemy.Column(sqlalchemy.String, nullable=False)
