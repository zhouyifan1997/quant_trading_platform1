from models.database_model.database_manager_base import *

class User(ModelBase):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String)
    username = Column(String)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)

    def __repr__(self) -> str:
        return "(%d, %s, %s, %s, %s, %s)" % \
            (self.user_id, self.email, self.username,  self.password, self.first_name, self.last_name)

class UserWatchListItem(ModelBase):
    __tablename__ = 'user_watch_list'

    user_id = Column(Integer, primary_key=True)
    stock_code = Column(Integer, primary_key=True)

class UserBuyListItem(ModelBase):
    __tablename__ = 'user_buy_list'

    user_id = Column(Integer, primary_key=True)
    stock_code = Column(Integer, primary_key=True)

class DatabaseManagerUser(DatabaseManagerBase):
    def __init__(self) -> None:
        super(DatabaseManagerUser, self).__init__()

    def get_user_info(self, email: str = None) -> Optional[User]:
        if email is None:
            return None
        session = self.session()
        res = session.query(User).filter(User.email == email).all()
        self.remove()
        return res[0] if len(res) == 1 else None

    def get_user_watch_stock(self, user_id: int) -> List[UserWatchListItem]:
        session = self.session()
        res = session.query(UserWatchListItem). \
            filter(UserWatchListItem.user_id == user_id).all()
        self.remove()
        return res

    def get_user_buy_stock(self, user_id: int) -> List[UserBuyListItem]:
        session = self.session()
        res = session.query(UserBuyListItem). \
            filter(UserBuyListItem.user_id == user_id).all()
        self.remove()
        return res
    
    def add_user_watch_stock(self, user_id: int, stock_code: str) -> None:
        self.add(UserWatchListItem(
            user_id=user_id,
            stock_code=stock_code,
        ))

    def add_user_buy_stock(self, user_id: int, stock_code: str) -> None:
        self.add(UserBuyListItem(
            user_id=user_id,
            stock_code=stock_code,
        ))

    def delete_user_watch_stock(self, user_id: int, stock_code: str) -> None:
        session = self.session()
        session.query(UserWatchListItem). \
            filter(UserWatchListItem.user_id == user_id). \
            filter(UserWatchListItem.stock_code == stock_code).delete()
        session.commit()
        self.remove()

    def delete_user_buy_stock(self, user_id: int, stock_code: str) -> None:
        session = self.session()
        session.query(UserBuyListItem). \
            filter(UserBuyListItem.user_id == user_id). \
            filter(UserBuyListItem.stock_code == stock_code).delete()
        session.commit()
        self.remove()
