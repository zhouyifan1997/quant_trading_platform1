from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Float,
    Integer,
    String,
    DateTime,
    create_engine,
    select,
    desc
)
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from typing import *

ModelBase = declarative_base()

class DatabaseManagerBase(object):
    def __init__(self) -> None:
        self._engine = create_engine('mysql+pymysql://clint:946983Yy2.2@127.0.0.1:3306/swing_trade_proto')
        self._session_factory = sessionmaker(bind=self._engine)
        self._Session = scoped_session(self._session_factory)

    def session(self):
        return self._Session()
    
    def remove(self) -> None:
        self._Session.remove()

    def add(self, obj: object) -> bool:
        session = self.session()
        try:
            session.add(obj)
            session.commit()
            self.remove()
            return True
        except:
            self.remove()
            return False

    def add_all(self, obj_list: List[object]) -> bool:
        try:
            session = self.session()
            session.bulk_save_objects(obj_list)
            session.commit()
            self.remove()
            return True
        except Exception as e:
            print(e)
            self.remove()
            return False        

    def execute(self, sql_query: str) -> None:
        try:
            with self._engine.connect() as connection:
                with connection.begin():
                    result = connection.execute(sql_query)
        except Exception as e:
            print(e)