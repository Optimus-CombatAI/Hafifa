# Stock Price Mining Exercise - Multithreading

This exercise is based on a real case where the information was used for research on predicting stock prices using Twitter. For more details, feel free to reach out to Tomer.

## Part 1

The stock we want to track for hourly changes from the provided list of hours is Bitcoin. You are required to use multithreading to write a CSV file containing the following columns: hour, stock type, and the percentage change (increase/decrease) of the stock.

### Recommendations:
- Use `ThreadPoolExecutor` for multithreaded operations.
- Use the `yahooFinance` library to fetch stock price data.
- Use `pandas` to write the results to a CSV file.

The name of the CSV file should be retrieved from an environment variable called `DESTINATION_FILE`, and the path to the file containing the hours should be read from another environment variable.

## Part 2

In the first part, we focused only on Bitcoin. Now, adapt your existing code to handle multiple stock types. In addition to Bitcoin, include the stocks for Google and Amazon, and save all the data into the same CSV file created in Part 1.

### Environment Variables:
- **Amazon**: `AMAZON_DATES` (file: `amazon_dates.txt`)
- **Google**: `GOOGLE_DATES` (file: `google_dates.txt`)
- **Bitcoin**: `BITCOIN_DATES` (file: `bitcoin_dates.txt`)

## Good Luck! (:

---

## This implementation

- `models.py` — `Stock` and `StockTask` data types
- `constants.py` — tracked stocks, CSV columns, log formats
- `logging_config.py` — stderr logging (`LOG_LEVEL`, default `INFO`; yfinance limited to errors)
- `config.py` — env vars, paths, hour files, `StockTask` list
- `stock_prices.py` — Yahoo fetch and hour-over-hour % change
- `pipeline.py` — `ThreadPoolExecutor` (one thread per stock), merge, CSV output
- `main.py` — bootstrap and orchestration

```bash
cd threading_multiprocessing
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
python main.py
```

Configure via `.env` (see `.env.example`). Paths are relative to this folder.

- Part 1: `DESTINATION_FILE`, `BITCOIN_DATES`
- Part 2: also `GOOGLE_DATES`, `AMAZON_DATES` (unset date vars are skipped)

Hours with no matching bar (or no previous bar) are omitted. Yahoo `1h` history is usually limited to ~730 days—timestamps outside that window often produce an empty CSV.
