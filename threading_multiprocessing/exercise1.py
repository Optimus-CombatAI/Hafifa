import os
import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta


def load_hours_from_file(file_path: str) -> list[str]:
    hours = []
    with open(file_path, "r") as file:
        for ligne in file:
            clean_line = ligne.strip()
            hours.append(clean_line)
    return hours


def fetch_bitcoin_price_at(timestamp: str) -> float | None:
    dt_start = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
    dt_end = dt_start + timedelta(hours=1)
    btc = yf.Ticker("BTC-USD")
    data = btc.history(start=dt_start, end=dt_end)

    if data.empty:
        return None

    price = float(data["Close"].iloc[0])
    return price


def fetch_prices_with_threads(hours: list[str]) -> list[tuple[str, float]]:
    results = []

    with ThreadPoolExecutor() as executor:
        future_to_hour = {
            executor.submit(fetch_bitcoin_price_at, hour): hour
            for hour in hours
        }

        for future, hour in future_to_hour.items():
            price = future.result()
            results.append((hour, price))

    return results


def calculate_percentage_changes(price_data: list[tuple[str, float]]) -> list[dict]:
    results = []

    for i in range(1, len(price_data)):
        timestamp, current_price = price_data[i]
        previous_timestamp, previous_price = price_data[i - 1]

        # Skip if one of the prices is None
        if current_price is None or previous_price is None:
            continue
        percentage_change = round(
            ((current_price - previous_price) / previous_price) * 100,
            4
        )

        results.append({
            "timestamp": timestamp,
            "current_price": current_price,
            "previous_timestamp": previous_timestamp,
            "previous_price": previous_price,
            "percentage_change": percentage_change
        })

    return results


def save_to_csv(rows: list[dict], destination_path: str) -> None:
    df = pd.DataFrame(rows)
    df.to_csv(destination_path, index=False)


def main():
    hours_file_path = os.getenv("HOURS_FILE")
    destination_file_path = os.getenv("DESTINATION_FILE")

    if not hours_file_path:
        print("error: HOURS_FILE is missing")
        return
    
    if not destination_file_path:
        print("error: DESTINATION_FILE is missing")
        return

    hours_list = load_hours_from_file(hours_file_path)
    prices = fetch_prices_with_threads(hours_list)
    rows = calculate_percentage_changes(prices)
    save_to_csv(rows, destination_file_path)


if __name__ == "__main__":
    main()
