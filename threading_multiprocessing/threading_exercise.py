from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import os

import yfinance as yf
import pandas as pd

################################################# PART 1 ########################################################

# #################################################################
# ### data on bitcoin changed and saved daily - so data is per day.
# ### im changing the task to read rows of dates (daily) and
# ### calculate the difference between one day to the follow day.
# #################################################################

# class Stock():

#     def __init__(self, stock_name = "bitcoin", workers_amount = 5):
#         self.stock_name = stock_name.upper()
#         self.workers_amount = workers_amount
#         self.dates_file_path = os.getenv(f"{stock_name}_DATASET") # name needs to be loaded from the env_variable.
#         # self.output_file_path = os.getenv("DESTINATION_FILE") # name needs to be loaded from the env_variable.
#         self.stock_changes = []
        
#         self.dates = self.read_dates_file()
#         self.stock_data = self.read_stock_data()

#     def read_dates_file(self) -> list[str]: # return list of dates.
#         dates = []
#         with open(self.dates_file_path, 'r') as dates_file:
#             for date in dates_file:
#                 dates.append(date.strip("\n").strip())
                
#         return dates

#     def get_stock_changes(self):
#         return self.stock_changes
    
#     def read_stock_data(self):
#         if self.stock_name == "BITCOIN":
#             return yf.Ticker("BTC-USD")
#         if self.stock_name == "AMAZON":
#             return yf.Ticker("AMZN-USD")
#         if self.stock_name == "GOOGLE":
#             return yf.Ticker("GOOGL-USD")
#         else:
#             raise Exception(f"No support for stock: {self.stock_name}")

#     def get_stock_prices(self, date: str) -> float: # return the stock price in specific date and a day after
#         end_date = datetime.fromisoformat(date) + timedelta(days=2)
#         end_date = end_date.strftime("%Y-%m-%d")
#         price = self.stock_data.history(interval="1D", start=date, end=end_date)
        
#         return float(price["Close"].iloc[0]), float(price["Close"].iloc[1])

#     # def write_stock_changes_csv_file(self):
#     #     csv_saver = pd.DataFrame(self.stock_changes)
#     #     csv_saver.to_csv(self.output_file_path, index=False)

#     def calculate_stock_changes(self, start_date) -> float: # return the change in percentage
#         end_date = datetime.fromisoformat(start_date) + timedelta(days=1)
#         end_date = end_date.strftime("%Y-%m-%d")
#         start_price, end_price = self.get_stock_prices(start_date)
#         self.stock_changes.append({
#             "Date": start_date,
#             "Stock": self.stock_name,
#             "Percentage": str(100 * (end_price - start_price) / start_price)
#         })
    
#     def main(self):
#         with ThreadPoolExecutor(max_workers=self.workers_amount) as executer:
#             executer.map(self.calculate_stock_changes, self.dates)
#         #self.write_stock_changes_csv_file()


# class StocksMine():
#     def __init__(self, stocks_list: list[Stock], workers_amount = 5):
#         self.workers_amount = workers_amount
#         self.stocks_list = stocks_list
#         self.output_file_path = os.getenv("DESTINATION_FILE") # name needs to be loaded from the env_variable.
        
#     def write_stocks_changes_csv_file(self):
#         stocks_changes = []
#         for stock in self.stocks_list:
#             stocks_changes.extend(stock.get_stock_changes)
#         csv_saver = pd.DataFrame(stocks_changes)
#         csv_saver.to_csv(self.output_file_path, index=False)
        
#     def run_stock_mine(self, stock: Stock):
#         stock.main()

#     def main(self):
#         with ThreadPoolExecutor(max_workers=self.workers_amount) as executer:
#             executer.map(self.run_stock_mine, self.stocks_list)
#         self.write_stocks_changes_csv_file()
    
# stocks = [Stock("bitcoin"), Stock("amazon"), Stock("google")]
# stocks_mine = StocksMine(stocks)
# stocks_mine.main()


################################################# PART 2 ########################################################

#################################################################
### data on bitcoin changed and saved daily - so data is per day.
### im changing the task to read rows of dates (daily) and
### calculate the difference between one day to the follow day.
#################################################################

class Stock():

    def __init__(self, stock_name = "bitcoin", workers_amount = 5):
        self.stock_name = stock_name.upper()
        self.workers_amount = workers_amount
        self.dates_file_path = f"{self.stock_name.lower()}_dates.txt"#os.getenv(f"{stock_name}_DATES") # name needs to be loaded from the env_variable.
        # self.output_file_path = os.getenv("DESTINATION_FILE") # name needs to be loaded from the env_variable.
        self.stock_changes = []
        
        self.dates = self.read_dates_file()
        self.stock_data = self.read_stock_data()

    def read_dates_file(self) -> list[str]: # return list of dates.
        dates = []
        with open(self.dates_file_path, 'r') as dates_file:
            for date in dates_file:
                dates.append(date.strip("\n").strip())
                
        return dates

    def get_stock_changes(self):
        return self.stock_changes
    
    def read_stock_data(self):
        if self.stock_name == "BITCOIN":
            return yf.Ticker("BTC-USD")
        if self.stock_name == "AMAZON":
            return yf.Ticker("AMZN-USD")
        if self.stock_name == "GOOGLE":
            return yf.Ticker("GOOGL-USD")
        else:
            raise Exception(f"No support for stock: {self.stock_name}")

    def get_stock_prices(self, date: str) -> float: # return the stock price in specific date and a day after
        end_date = datetime.fromisoformat(date) + timedelta(days=2)
        end_date = end_date.strftime("%Y-%m-%d")
        price = self.stock_data.history(interval="1D", start=date, end=end_date)
        
        return float(price["Close"].iloc[0]), float(price["Close"].iloc[1])

    # def write_stock_changes_csv_file(self):
    #     csv_saver = pd.DataFrame(self.stock_changes)
    #     csv_saver.to_csv(self.output_file_path, index=False)

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
        #self.write_stock_changes_csv_file()


class StocksMine():
    def __init__(self, stocks_list: list[Stock], workers_amount = 5):
        self.workers_amount = workers_amount
        self.stocks_list = stocks_list
        self.output_file_path = os.getenv("DESTINATION_FILE") # name needs to be loaded from the env_variable.
        
    def write_stocks_changes_csv_file(self):
        stocks_changes = []
        for stock in self.stocks_list:
            stocks_changes.extend(stock.get_stock_changes())
        csv_saver = pd.DataFrame(stocks_changes)
        csv_saver.to_csv(self.output_file_path, index=False)
        
    def run_stock_mine(self, stock: Stock):
        stock.main()

    def main(self):
        with ThreadPoolExecutor(max_workers=self.workers_amount) as executer:
            executer.map(self.run_stock_mine, self.stocks_list)
        self.write_stocks_changes_csv_file()
    
stocks = [Stock("bitcoin"), Stock("amazon"), Stock("google")]
stocks_mine = StocksMine(stocks)
stocks_mine.main()
