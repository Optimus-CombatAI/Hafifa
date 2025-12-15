from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import os

import yfinance as yf
import pandas as pd


#################################################################
### data on bitcoin changed and saved daily - so data is per day.
### im changing the task to read rows of dates (daily) and
### calculate the difference between one day to the follow day.
#################################################################

class StockMine():

    def __init__(self, stock_name = "bitcoin", workers_amount = 5):
        self.stock_name = stock_name
        self.workers_amount = workers_amount
        self.dates_file_path = os.getenv(stock_name.upper()) # name needs to be loaded from the env_variable.
        self.output_file_path = os.getenv("DESTINATION_FILE") # name needs to be loaded from the env_variable.
        self.stock_changes = []
        
        self.dates = self.read_dates_file()
        self.stock_data = self.read_stock_data()

    def read_dates_file(self) -> list[str]: # return list of dates.
        dates = []
        with open(self.dates_file_path, 'r') as dates_file:
            for date in dates_file:
                dates.append(date.strip("\n").strip())
                
        return dates

    def read_stock_data(self):
        return yf.Ticker("BTC-USD")

    def get_stock_prices(self, date: str) -> float: # return the stock price in specific date and a day after
        end_date = datetime.fromisoformat(date) + timedelta(days=2)
        end_date = end_date.strftime("%Y-%m-%d")
        price = self.stock_data.history(interval="1D", start=date, end=end_date)
        
        return float(price["Close"].iloc[0]), float(price["Close"].iloc[1])

    def write_stock_changes_csv_file(self):
        csv_saver = pd.DataFrame(self.stock_changes)
        csv_saver.to_csv(self.output_file_path, index=False)

    def calculate_stock_changes(self, start_date) -> float: # return the change in percentage
        end_date = datetime.fromisoformat(start_date) + timedelta(days=1)
        end_date = end_date.strftime("%Y-%m-%d")
        start_price, end_price = self.get_stock_prices(start_date)
        self.stock_changes.append({
            "Date": start_date,
            "Stock": self.stock_name,
            "Percentage": str(100 * (end_price - start_price) / start_price)
        })
    
    def main(self):
        with ThreadPoolExecutor(max_workers=self.workers_amount) as executer:
            executer.map(self.calculate_stock_changes, self.dates)
        self.write_stock_changes_csv_file()

stock_mine = StockMine()
stock_mine.main()
