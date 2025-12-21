from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
import pandas as pd

from db.database import Base


class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='CASCADE'))
    pm2_5 = Column(Integer)
    no2 = Column(Integer)
    co2 = Column(Integer)
    overall_aqi = Column(Integer)
    aqi_level = Column(String)

    city = relationship("City", back_populates="reports")
