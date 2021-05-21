from models.database_model.database_manager import *
from utils.date_model import DateModel

if __name__ == "__main__":
    database_manager = DatabaseManager()
    date_model = DateModel()
    recommendation_list = database_manager.get_recommendation_stock_list()
    start = '2015-01-01'
    end = '2020-12-31'
    while start != end:
        for stock in recommendation_list:
            basic_info = database_manager.get_stock_basic_info(stock.stock_code, start)
            ema_info = database_manager.get_stock_ema_info(stock.stock_code, start)

        for stock in recommendation_list:
            basic_info = database_manager.get_stock_basic_info(stock.stock_code, start)
            ema_info = database_manager.get_stock_ema_info(stock.stock_code, start)

        for stock in recommendation_list:
            basic_info = database_manager.get_stock_basic_info(stock.stock_code, start)
            ema_info = database_manager.get_stock_ema_info(stock.stock_code, start)
        start = date_model.get_next_week_day(start)
        print(start)