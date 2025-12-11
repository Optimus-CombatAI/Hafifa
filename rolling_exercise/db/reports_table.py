from sqlalchemy import Table, Column, Integer, String, Date, ForeignKey
from consts import META_DATA


reports = Table(
    'reports', META_DATA,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('date', Date),
    Column('city_id', Integer, ForeignKey('cities.id', ondelete='CASCADE')),
    Column('pm2_5', Integer),
    Column('no2', Integer),
    Column('co2', Integer),
    Column('overall_aqi', Integer),
    Column('aqi_level', String),
)
