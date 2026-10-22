import pandas as pd
import pytest

from stock_prices import hourly_closes, parse_hours, percentage_changes


def make_closes(closes_by_hour: dict[str, float]) -> pd.Series:
    return pd.Series(list(closes_by_hour.values()), index=pd.to_datetime(list(closes_by_hour)))


def test_parse_hours_floors_to_hour_and_drops_invalid_lines():
    requested = parse_hours(["2026-01-01 10:15:59.919316", "not a date"])

    assert requested["hour"].tolist() == ["2026-01-01 10:15:59.919316"]
    assert requested["bar"].tolist() == [pd.Timestamp("2026-01-01 10:00")]


def test_hourly_closes_keeps_last_close_per_utc_hour():
    index = pd.DatetimeIndex(
        ["2026-01-01 10:00", "2026-01-01 10:30", "2026-01-01 11:00"], tz="America/New_York"
    )
    history = pd.DataFrame({"Close": [1.0, 2.0, 3.0]}, index=index)

    assert hourly_closes(history).to_dict() == {
        pd.Timestamp("2026-01-01 15:00"): 2.0,
        pd.Timestamp("2026-01-01 16:00"): 3.0,
    }


def test_hourly_closes_of_empty_history_is_empty():
    assert hourly_closes(pd.DataFrame()).empty


def test_percentage_changes_compares_with_previous_calendar_hour():
    closes = make_closes(
        {"2026-01-01 09:00": 100.0, "2026-01-01 10:00": 110.0, "2026-01-01 12:00": 99.0}
    )
    requested = parse_hours(["2026-01-01 10:20", "2026-01-01 12:05"])

    result = percentage_changes(closes, requested, "Bitcoin")

    assert result["hour"].tolist() == ["2026-01-01 10:20"]
    assert result["stock type"].tolist() == ["Bitcoin"]
    assert result["percentage change"].tolist() == pytest.approx([10.0])


def test_percentage_changes_skips_zero_previous_close():
    closes = make_closes({"2026-01-01 09:00": 0.0, "2026-01-01 10:00": 5.0})

    result = percentage_changes(closes, parse_hours(["2026-01-01 10:00"]), "Bitcoin")

    assert result.empty
