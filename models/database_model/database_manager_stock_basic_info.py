from models.database_model.database_manager_base import *

class StockBasicInfo(ModelBase):
    __tablename__ = 'stock_basic_info'

    stock_basic_info_id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String)
    stock_info_date = Column(String)
    open = Column(Float)
    close = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(Float)

    def __repr__(self) -> str:
        return "(%s, %s, %.4f, %.4f, %.4f, %.4f, %.4f)" % (self.stock_code, self.stock_info_date, self.open, self.close, self.high, self.low, self.volume)

    def to_json(self) -> Dict[str, Union[str, float]]:
        return {
            "stock_code": self.code,
            "date": self.date,
            "open": self.open,
            "close": self.close,
            "high": self.high,
            "low": self.low,
            "volume": self.volume   
        }

class DatabaseManagerStockBasicInfo(DatabaseManagerBase):
    def __init__(self) -> None:
        super(DatabaseManagerStockBasicInfo, self).__init__()

    def get_stock_basic_info(self, stock_code: str, date: str) -> Optional[StockBasicInfo]:
        session = self.session()
        res = session.query(StockBasicInfo). \
        filter(StockBasicInfo.stock_code == stock_code). \
        filter(StockBasicInfo.stock_info_date == date).all()
        self.remove()
        return res[0] if len(res) > 0 else None