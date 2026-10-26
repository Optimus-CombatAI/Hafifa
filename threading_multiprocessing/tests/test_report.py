import pandas as pd
import pytest

from domain.models import Stock, StockTicker
from domain.report import build_changes_table, format_requested_hour, hourly_percentage_change
from tests.helpers import ohlcv_bars


def test_format_requested_hour_keeps_microseconds():
    timestamp = pd.Timestamp("2026-03-17 16:15:59.919316")
    assert format_requested_hour(timestamp) == "2026-03-17 16:15:59.919316"


def test_hourly_percentage_change_uses_first_bar_on_or_after_hour_floor():
    bars = ohlcv_bars(
        "2026-03-17 15:30:00",
        "2026-03-17 16:30:00",
        close=[100.0, 99.99765765767052],
    )
    requested = pd.Timestamp("2026-03-17 16:15:59.919316")

    change = hourly_percentage_change(bars, requested)

    assert change == pytest.approx(-0.0023423423294754997)


def test_build_changes_table_merges_all_stocks():
    bitcoin = Stock(
        StockTicker.BITCOIN,
        pd.DatetimeIndex([pd.Timestamp("2026-03-17 19:15:59.919316")]),
        ohlcv_bars(
            "2026-03-17 18:00:00",
            "2026-03-17 19:00:00",
            close=[100.0, 99.775752007560928],
        ),
    )
    amazon = Stock(
        StockTicker.AMAZON,
        pd.DatetimeIndex([pd.Timestamp("2026-03-17 16:15:59.919316")]),
        ohlcv_bars(
            "2026-03-17 15:30:00",
            "2026-03-17 16:30:00",
            close=[100.0, 99.99765765767052],
        ),
    )

    table = build_changes_table([bitcoin, amazon])

    assert list(table.columns) == ["hour", "stock type", "percentage change"]
    assert set(table["stock type"]) == {"Bitcoin", "Amazon"}
    assert len(table) == 2
