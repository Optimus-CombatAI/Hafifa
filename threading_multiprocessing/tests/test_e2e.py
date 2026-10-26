"""Hits the real Yahoo Finance API. Run with ``pytest -m integration``."""

import pytest

from domain.load import load_stocks
from domain.models import StockTicker
from domain.pipeline import run_pipeline
from domain.report import write_destination_csv

pytestmark = pytest.mark.integration


def test_pipeline_fetches_bitcoin(tmp_path):
    [stock] = run_pipeline(load_stocks([StockTicker.BITCOIN]), tmp_path, max_workers=4)

    assert (tmp_path / "BTC-USD.csv").is_file()
    assert stock.data["Close"].notna().any()

    destination = tmp_path / "changes.csv"
    changes = write_destination_csv([stock], destination)
    assert destination.is_file()
    assert list(changes.columns) == ["hour", "stock type", "percentage change"]
    assert (changes["stock type"] == "Bitcoin").all()


def test_pipeline_fetches_all_stocks(tmp_path):
    stocks = run_pipeline(load_stocks(), tmp_path, max_workers=8)

    assert {stock.ticker for stock in stocks} == set(StockTicker)
    for stock in stocks:
        assert (tmp_path / f"{stock.ticker.value}.csv").is_file()
