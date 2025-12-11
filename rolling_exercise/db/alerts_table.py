from sqlalchemy import Table, Column, Integer, String, Date, ForeignKey

from consts import META_DATA

alerts = Table(
    'alerts', META_DATA,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('date', Date),
    Column('city_id', Integer, ForeignKey('cities.id', ondelete='CASCADE')),
    Column('overall_aqi', Integer),
    Column('aqi_level', String),
)
