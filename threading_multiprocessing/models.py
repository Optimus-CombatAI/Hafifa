"""Data types shared across modules."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Stock:
    name: str
    ticker: str
    dates_env: str


@dataclass(frozen=True)
class StockTask:
    stock: Stock
    hours: tuple[str, ...]

    @property
    def label(self) -> str:
        return f"{self.stock.name} ({self.stock.ticker})"
