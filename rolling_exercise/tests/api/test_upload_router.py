from pathlib import Path

import pytest
from fastapi import status
from httpx import Response

from tests.api.uploads import UPLOAD_URL, upload_content, upload_rows
from tests.csv_rows import csv_row


@pytest.fixture
def sample_files_dir(request) -> Path:
    return request.config.rootpath / "air_quality_files"


def rejected_lines(response: Response) -> list[int]:
    return [rejected_row["line_number"] for rejected_row in response.json()["rejected_rows"]]


def test_upload_saves_valid_rows_and_reports_invalid_ones(client):
    response = upload_rows(client, csv_row(city="Haifa"), csv_row(city="Akko", no2=""))

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["saved_rows"] == 1
    assert rejected_lines(response) == [3]


def test_rows_from_an_earlier_upload_are_rejected_as_duplicates(client):
    upload_rows(client, csv_row(date="2024-11-19", city="Haifa"))

    response = upload_rows(client, csv_row(date="2024-11-19", city="Haifa"))

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["saved_rows"] == 0
    assert rejected_lines(response) == [2]


def test_real_sample_file_is_accepted(client, sample_files_dir):
    sample_file = sample_files_dir / "air_quality_2024_11_19.csv"

    response = upload_content(client, sample_file.name, sample_file.read_bytes())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["saved_rows"] > 0


def test_unusable_file_returns_bad_request_with_reason(client):
    response = upload_content(client, "empty.csv", b"")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "File is empty"}


def test_request_without_file_is_unprocessable(client):
    response = client.post(UPLOAD_URL)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
