from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from db.pgDatabase import Base


class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    reports = relationship("Report", back_populates="city")
