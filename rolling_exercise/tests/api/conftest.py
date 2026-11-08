import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.configs.settings import ApiSettings

ALERT_AQI_THRESHOLD = 300


@pytest.fixture
def client(tmp_path) -> TestClient:
    settings = ApiSettings(
        log_file_path=tmp_path / "test.log",
        database_url=f"sqlite:///{(tmp_path / 'test.db').as_posix()}",
        alert_aqi_threshold=ALERT_AQI_THRESHOLD,
        api_host="127.0.0.1",
        api_port=8000,
    )

    return TestClient(create_app(settings))
