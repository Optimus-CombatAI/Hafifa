from fastapi.testclient import TestClient
from httpx import Response

from tests.csv_rows import to_csv

UPLOAD_URL = "/air-quality/upload"


def upload_content(client: TestClient, file_name: str, file_content: bytes) -> Response:
    return client.post(UPLOAD_URL, files={"file": (file_name, file_content, "text/csv")})


def upload_rows(client: TestClient, *rows: str) -> Response:
    return upload_content(client, "air_quality.csv", to_csv(*rows))
