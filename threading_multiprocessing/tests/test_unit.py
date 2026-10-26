import pandas as pd
import pytest

from core.constant import FETCH_BATCH_SIZE, FETCH_PADDING
from domain.client import YahooFetchError
from domain.load import load_stocks
from domain.models import Stock, StockTicker
from domain.pipeline import merge_ohlcv, plan_windows, run_pipeline
from tests.helpers import ohlcv_bars


def test_load_stocks_skips_bad_lines_and_preserves_timestamps(tmp_path):
    hours_file = tmp_path / "hours.txt"
    hours_file.write_text(
        "2024-01-01 11:15:59.919316\n\nnot a date\n2024-01-01 10:45:00\n"
    )

    [stock] = load_stocks(
        [StockTicker.BITCOIN], hours_files={StockTicker.BITCOIN: hours_file}
    )

    assert stock.name == "Bitcoin"
    assert list(stock.hours) == [
        pd.Timestamp("2024-01-01 10:45:00"),
        pd.Timestamp("2024-01-01 11:15:59.919316"),
    ]
    assert stock.data.empty


def test_plan_windows_splits_hours_into_padded_batches():
    hours = pd.date_range("2024-01-01", periods=5, freq="h")

    windows = plan_windows(hours, batch_size=2)

    assert len(windows) == 3
    assert windows[0] == (hours[0] - FETCH_PADDING, hours[1] + FETCH_PADDING)
    assert windows[2][0] == hours[4] - FETCH_PADDING


def test_plan_windows_without_hours_is_empty():
    assert plan_windows(pd.DatetimeIndex([])) == []


def test_merge_ohlcv_keeps_the_latest_duplicate():
    merged = merge_ohlcv(
        ohlcv_bars("2024-01-01 10:00", close=1.0),
        ohlcv_bars("2024-01-01 10:00", "2024-01-01 11:00", close=2.0),
    )

    assert list(merged["Close"]) == [2.0, 2.0]


def test_run_pipeline_merges_batches_into_one_csv_per_ticker(tmp_path):
    hours = pd.date_range("2024-01-01", periods=FETCH_BATCH_SIZE + 1, freq="h")

    def fake_fetch(ticker, start, end):
        return ohlcv_bars(str(start + FETCH_PADDING))

    [stock] = run_pipeline(
        [Stock(StockTicker.BITCOIN, hours)], tmp_path, max_workers=2, fetch=fake_fetch
    )

    assert list(stock.data.index) == [hours[0], hours[FETCH_BATCH_SIZE]]
    assert (tmp_path / "BTC-USD.csv").is_file()


def test_run_pipeline_raises_when_fetch_returns_empty(tmp_path):
    hours = pd.date_range("2024-01-01", periods=2, freq="h")

    def empty_fetch(ticker, start, end):
        return ohlcv_bars()

    with pytest.raises(YahooFetchError, match="No bars fetched"):
        run_pipeline(
            [Stock(StockTicker.BITCOIN, hours)],
            tmp_path,
            max_workers=1,
            fetch=empty_fetch,
        )
