from sqlalchemy import Table, Column, Integer, String, Date, ForeignKey, UniqueConstraint, MetaData


def _define_reports_table(metadata: MetaData) -> Table:
    reports = Table(
        'reports', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('date', Date, nullable=False),
        Column('city_id', Integer, ForeignKey('cities.id', ondelete='CASCADE')),
        Column('pm2_5', Integer, nullable=False),
        Column('no2', Integer, nullable=False),
        Column('co2', Integer, nullable=False),
        Column('overall_aqi', Integer, index=True, nullable=False),
        Column('aqi_level', String, nullable=False),

        UniqueConstraint('date', 'city_id'),
    )

    return reports
