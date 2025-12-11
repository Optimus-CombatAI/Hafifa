from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from consts import BASE


class Alert(BASE):
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='CASCADE'))
    overall_aqi = Column(Integer)
    aqi_level = Column(String)

    city = relationship("City", back_populates="alerts")


