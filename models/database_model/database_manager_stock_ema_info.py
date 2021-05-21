from models.database_model.database_manager_base import *

class StockEMAInfo(ModelBase):
    __tablename__ = 'stock_ema_info'

    stock_ema_info_id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String)
    stock_info_date = Column(String)
    one = Column(Float)
    two = Column(Float)
    three = Column(Float)
    four = Column(Float)
    five = Column(Float)

    def __repr__(self) -> str:
        return "(%s, %s, %.4f, %.4f, %.4f, %.4f, %.4f)" % (self.stock_code, self.stock_info_date, self.one, self.two, self.three, self.four, self.five)

    def to_json(self) -> Dict[str, Union[str, float]]:
        return {
            "stock_code": self.code,
            "date": self.date,
            "ema5": self.one,
            "ema13": self.two,
            "ema35": self.three,
            "ema55": self.four,
            "ema233": self.five
        }

class DatabaseManagerStockEMAInfo(DatabaseManagerBase):
    def __init__(self) -> None:
        super(DatabaseManagerStockEMAInfo, self).__init__()

    def get_stock_ema_info(self, stock_code: str, date: str) -> Optional[StockEMAInfo]:
        session = self.session()
        res = session.query(StockEMAInfo). \
        filter(StockEMAInfo.stock_code == stock_code). \
        filter(StockEMAInfo.stock_info_date == date).all()
        self.remove()
        return res[0] if len(res) > 0 else None