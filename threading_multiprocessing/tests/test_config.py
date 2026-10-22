import pytest

from config import ConfigError, load_stock_tasks, require_destination
from constant import STOCKS


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv("DESTINATION_FILE", raising=False)
    for stock in STOCKS:
        monkeypatch.delenv(stock.dates_env, raising=False)


def test_load_stock_tasks_reads_only_configured_stocks(monkeypatch, tmp_path):
    hours_file = tmp_path / "bitcoin.txt"
    hours_file.write_text("2026-01-01 10:00\n\n  2026-01-01 11:00  \n", encoding="utf-8")
    monkeypatch.setenv("BITCOIN_DATES", str(hours_file))

    [task] = load_stock_tasks()

    assert task.stock.ticker == "BTC-USD"
    assert task.hours == ("2026-01-01 10:00", "2026-01-01 11:00")


def test_load_stock_tasks_without_any_dates_env_fails():
    with pytest.raises(ConfigError, match="No hour files configured"):
        load_stock_tasks()


def test_load_stock_tasks_with_missing_file_names_the_env_var(monkeypatch, tmp_path):
    monkeypatch.setenv("GOOGLE_DATES", str(tmp_path / "missing.txt"))

    with pytest.raises(ConfigError, match="GOOGLE_DATES"):
        load_stock_tasks()


def test_require_destination_without_env_fails():
    with pytest.raises(ConfigError, match="DESTINATION_FILE"):
        require_destination()
