#!/usr/bin/python3
import csv
import random
import threading
import time
import timeit

from models.database_model.database_manager import *
from models.api_query_model.stock_basic_info_query_model import *
from models.api_query_model.ema_query_model import *
from models.swing_trade_model.swing_trade_model import *
from utils.date_model import *


class InsertThread(threading.Thread):
    def __init__(self, database_generator: object, stock: str):
        threading.Thread.__init__(self)
        self._database_generator = database_generator
        self._stock = stock
    def run(self):
        self._database_generator.insert_stock(self._stock)

class UpdateThread(threading.Thread):
    def __init__(self, database_generator: object, stock: str):
        threading.Thread.__init__(self)
        self._database_generator = database_generator
        self._stock = stock
    def run(self):
        self._database_generator.update_stock(self._stock)

class DatabaseGenerator:
    def __init__(self):
        self._database_manager = DatabaseManager.get_instance()
        self._swing_trade_model = SwingTradeModel()
        self._date_model = DateModel()
        self._thread_lock = threading.Lock()
        self._insert_stock_lock = threading.Lock()
        self._stock_basic_info_list: List[StockBasicInfo] = []
        self._stock_ema_info_list: List[EMAInfo] = []

    def insert_stock(self, stock_code: str) -> None:
        print("Inserting", stock_code)
        self._database_manager.insert_stock(stock_code)
        self._update_stock_basic_info(stock_code)
        self._update_stock_ema_info(stock_code)

    def update_stock(self, stock_code: str) -> None:
        print("Updating", stock_code)
        self._update_stock_basic_info(stock_code)
        self._update_stock_ema_info(stock_code)
    
    def _update_stock_basic_info(self, stock_code: str) -> None:
        stock_basic_info_list, is_valid_stock = query_basic_info(stock_code)
        while stock_basic_info_list is None and is_valid_stock:
            print("Hitting API usage limit, sleeping")
            time.sleep(10)
            stock_basic_info_list, is_valid_stock = query_basic_info(stock_code)
        print('Finished querying basic_info for', stock_code)
        if not is_valid_stock:
            return
        self._database_manager.add_stock_basic_info_list(stock_code, stock_basic_info_list)

    def _update_stock_ema_info(self, stock_code: str) -> None:
        stock_ema_info_list, is_valid_stock = query_ema_values(stock_code)
        while stock_ema_info_list is None and is_valid_stock:
            print("Hitting API usage limit, sleeping")
            time.sleep(10)
            stock_ema_info_list, is_valid_stock = query_ema_values(stock_code)
        print('Finished querying ema_info for', stock_code)
        if not is_valid_stock:
            return
        self._database_manager.add_stock_ema_info_list(stock_code, stock_ema_info_list)
    
    def init_stock_list(self) -> None:
        with open('./script/database_script/stock.txt', 'r') as f:
            for row in f:
                stock = row.replace("\n", "").upper()
                self._database_manager.insert_stock(stock)

    def init_recommendation_stock_list(self) -> None:
        with open('./script/database_script/recommendation_stock.txt', 'r') as f:
            for row in f:
                stock = row.replace("\n", "").upper()
                self._database_manager.insert_recommendation_stock(stock)

    def generate_database(self) -> None:
        start = timeit.default_timer()
        self._database_manager.init()
        self.init_stock_list()
        self.init_recommendation_stock_list()
        thread_list = []
        count = 0
        for stock in self._database_manager.get_stock_list():
            if len(thread_list) == 30:
                for thread in thread_list:
                    thread.join()
                    count += 1
                    print(count, "joined")
                thread_list = []
            thread = InsertThread(self, stock.stock_code)
            thread.start()
            thread_list.append(thread)
            
        for thread in thread_list:
            thread.join()
            count += 1

        stop = timeit.default_timer()
        print('Time: ', stop - start)  

    def update_database(self) -> None:
        start = timeit.default_timer()
        thread_list = []
        count = 0
        for stock in self._database_manager.get_stock_list():
            if len(thread_list) == 30:
                for thread in thread_list:
                    thread.join()
                    count += 1
                    print(count, "joined")
                thread_list = []
            thread = UpdateThread(self, stock.stock_code)
            thread.start()
            thread_list.append(thread)

        for thread in thread_list:
            thread.join()
            count += 1

        stop = timeit.default_timer()
        print('Time: ', stop - start)  

    def drop_database(self) -> None:
        self._database_manager.destroy()

if __name__ == "__main__":
    generator = DatabaseGenerator()
    generator.drop_database()
    generator.generate_database()