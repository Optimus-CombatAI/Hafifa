from dotenv import load_dotenv
import logging
import os

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BASE = declarative_base()

load_dotenv()

META_DATA = MetaData()

LOG_FILENAME = "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filename=LOG_FILENAME,
    filemode="a"  # append
)

LOGGER = logging.getLogger("app")
LOGGER.setLevel(logging.INFO)

handler = logging.FileHandler(LOG_FILENAME)
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
LOGGER.addHandler(handler)

alchemy_logger = logging.getLogger("sqlalchemy.engine")
alchemy_logger.propagate = True
alchemy_logger.setLevel(logging.INFO)

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
DB = "prepSQL"
SCHEME = "rolling_exercise"

ENGINE = create_engine(
    f"postgresql://{USER}:{PASSWORD}@localhost/{DB}?options=-csearch_path={SCHEME}",
    echo=False
)

Session = sessionmaker(bind=ENGINE)
SESSION = Session()

USE_DUMMY_DATASET = False
USE_DATA_FILL = True
DATA_PATH = os.getenv("DATA_PATH")
METHOD = "from_data"

PM25_MEDIAN = 15
PM25_SIGMA = 0.8

NO2_MEDIAN = 30
NO2_SIGMA = 0.7

CO2_MEAN = 420
CO2_STD = 50
