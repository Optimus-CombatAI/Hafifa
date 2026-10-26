import pandas as pd

from core.config import Config
from core.constant import PACKAGE_DIR
from domain.load import load_stocks
from domain.models import StockTicker


def test_destination_file_is_placed_in_output_dir():
    config = Config(
        _env_file=None,
        destination_file="stock_changes.csv",
        output_dir="data/processed",
    )

    assert config.destination_file == PACKAGE_DIR / "data" / "processed" / "stock_changes.csv"


def test_load_stocks_reads_hours_dir(tmp_path):
    (tmp_path / "BTC-USD.txt").write_text("2024-01-01 10:00:00\n")

    [stock] = load_stocks([StockTicker.BITCOIN], hours_dir=tmp_path)

    assert list(stock.hours) == [pd.Timestamp("2024-01-01 10:00:00")]


def test_load_stocks_honors_dates_override(tmp_path):
    custom = tmp_path / "custom.txt"
    custom.write_text("2024-02-01 11:00:00\n")
    config = Config(_env_file=None, bitcoin_dates=custom)

    [stock] = load_stocks([StockTicker.BITCOIN], config=config)

    assert list(stock.hours) == [pd.Timestamp("2024-02-01 11:00:00")]
