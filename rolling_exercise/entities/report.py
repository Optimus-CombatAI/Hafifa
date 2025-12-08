from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from consts import BASE


class Report(BASE):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True)
    date = Column(String)
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='CASCADE'))
    pm2_5 = Column(Integer)
    no2 = Column(Integer)
    co2 = Column(Integer)
    aqi = Column(Integer)

    city = relationship("City", back_populates="reports")

