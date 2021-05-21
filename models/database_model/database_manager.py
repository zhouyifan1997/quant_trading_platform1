from models.database_model.database_manager_base import *
from models.database_model.database_manager_stock_basic_info import *
from models.database_model.database_manager_stock_ema_info import *
from models.database_model.database_manager_user import *
from utils.date_model import DateModel

from constants.sql_query_constant import (
    DESTROY_DATABASE_QUERY,
    INIT_DATABASE_QUERY,
)

import timeit

class Stock(ModelBase):
    __tablename__ = 'stock'

    stock_code = Column(String, primary_key=True)

class RecommendationStock(ModelBase):
    __tablename__ = 'recommendation_stock_list'

    stock_code = Column(String, primary_key=True)


class DatabaseManager(
    DatabaseManagerStockBasicInfo,
    DatabaseManagerStockEMAInfo,
    DatabaseManagerUser,
):
    """Database Manager is a Singleton"""
    __instance = None

    @staticmethod
    def get_instance():
        if DatabaseManager.__instance is None:
            DatabaseManager()
        return DatabaseManager.__instance

    def __init__(self) -> None:
        super(DatabaseManager, self).__init__()
        DatabaseManager.__instance = self
        self._date_model = DateModel()

    def insert_stock(self, stock_code: str) -> None:
        self.add(Stock(
            stock_code=stock_code
        ))

    def insert_recommendation_stock(self, stock_code: str) -> None:
        self.insert_stock(stock_code)
        self.add(RecommendationStock(
            stock_code=stock_code
        ))
        
    def get_stock_list(self) -> List[Stock]:
        session = self.session()
        res = session.query(Stock).all()
        self.remove()
        return res

    def get_recommendation_stock_list(self) -> List[RecommendationStock]:
        session = self.session()
        res = session.query(RecommendationStock).all()
        self.remove()
        return res

    def get_last_updated_stock_basic_info_date(self, stock_code: str) -> Optional[str]:
        session = self.session()
        result = session.query(StockBasicInfo.stock_info_date).filter(StockBasicInfo.stock_code == stock_code). \
            order_by(desc(StockBasicInfo.stock_info_date)).all()
        self.remove()
        return None if len(result) == 0 else self._date_model.to_str(result[0][0])

    def get_last_updated_stock_ema_info_date(self, stock_code: str) -> Optional[str]:
        session = self.session()
        result = session.query(StockEMAInfo.stock_info_date).filter(StockEMAInfo.stock_code == stock_code). \
            order_by(desc(StockEMAInfo.stock_info_date)).all()
        self.remove()
        return None if len(result) == 0 else self._date_model.to_str(result[0][0])

    def is_valid_verification_stock(self, stock_code: str, start_date: str) -> bool:
        return self.get_stock_ema_info(stock_code, start_date) is not None

    def add_stock_basic_info_list(self, stock_code: str, stock_basic_info_list: List[StockBasicInfo]) -> None:
        last_updated_stock_basic_info_date = self.get_last_updated_stock_basic_info_date(stock_code)
        filtered_stock_basic_info_list = stock_basic_info_list if last_updated_stock_basic_info_date is None else \
            list(filter(lambda stock_basic_info: stock_basic_info.stock_info_date > last_updated_stock_basic_info_date, stock_basic_info_list))
        self.add_all(filtered_stock_basic_info_list)

    def add_stock_ema_info_list(self, stock_code: str, stock_ema_info_list: List[StockEMAInfo]) -> None:
        last_updated_stock_ema_info_date = self.get_last_updated_stock_ema_info_date(stock_code)
        filtered_stock_ema_info_list = stock_ema_info_list if last_updated_stock_ema_info_date is None else \
            list(filter(lambda stock_ema_info: stock_ema_info.stock_info_date > last_updated_stock_ema_info_date, stock_ema_info_list))
        self.add_all(filtered_stock_ema_info_list)

    def init(self) -> None:
        for row in INIT_DATABASE_QUERY:
            self.execute(row)

    def destroy(self) -> None:
        for row in DESTROY_DATABASE_QUERY:
            self.execute(row)