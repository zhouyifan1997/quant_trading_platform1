from flask import (
    Flask, 
    abort,
    request,
)
from flask_cors import (
    CORS,
    cross_origin,
)
from flask_restful import (
    Resource, 
    Api,
)

import datetime
from functools import wraps
import hashlib
import jwt
import json
import time
from typing import *
import uuid
import threading
from werkzeug.security import safe_str_cmp

from models.api_query_model.ema_query_model import *
from models.api_query_model.stock_basic_info_query_model import *
from models.database_model.database_manager import *
from models.swing_trade_model.swing_trade_model import *

from utils.date_model import *

# decorator for verifying the JWT 
def token_required(f): 
    @wraps(f) 
    def decorated(*args, **kwargs): 
        token = None
        # jwt is passed in the request header 
        if 'Authorization' in request.headers: 
            token = request.headers['Authorization'] 
        # return 401 if token is not passed 
        if not token: 
            abort(401)
   
        try: 
            # decoding the payload to fetch the stored details 
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithm="HS256")
        except Exception as e:
            print(e) 
            abort(401)
        # returns the current logged in users contex to the routes 
        return  f(*args, **kwargs) 
    return decorated

def encrypt_string(hash_string: str) -> str:
    sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature


class InsertNewStockThread(threading.Thread):
    def __init__(self, user_id: int, stock_code: str):
        threading.Thread.__init__(self)
        self._user_id = user_id
        self._stock_code = stock_code

    def run(self) -> None:
        user_id = self._user_id
        stock_code = self._stock_code
        basic_info, is_valid_basic = query_basic_info(stock_code)
        while is_valid_basic and basic_info is None:
            time.sleep(1)
            basic_info, is_valid_basic = query_basic_info(stock_code)
        if not is_valid_basic:
            return False
        database_manager.insert_stock(stock_code)
        database_manager.add_user_watch_stock(user_id, stock_code)
        database_manager.add_stock_basic_info_list(stock_code, basic_info)
        ema_info, is_valid_ema = query_ema_values(stock_code)
        while ema_info is None and is_valid_ema:
            time.sleep(1)
            ema_info, is_valid_ema = query_ema_values(stock_code)
        if is_valid_ema:
            database_manager.add_stock_ema_info_list(stock_code, ema_info)

def insert_if_not_exist(user_id: int, stock_code: str) -> bool:
    basic_info = database_manager.get_stock_basic_info(stock_code, date_model.get_today())
    if basic_info is not None:
        database_manager.add_user_watch_stock(user_id, stock_code)
        return True
    thread = InsertNewStockThread(user_id, stock_code)
    thread.start()
    return True
    

def stock_code_to_strategy_info(stock_code: str, date: str = '') -> Dict[str, str]:
    def trade_action_to_str(trade_action: TradeAction):
        if trade_action == TradeAction.BUY:
            return 'BUY'
        elif trade_action == TradeAction.SELL:
            return 'SELL'
        else:
            return 'PASS'
    date = date_model.get_today() if date == '' else date
    trade_strategy = swing_trade_model.determine_strategy(stock_code, date)
    trade_action = trade_action_to_str(trade_strategy.action)
    return {
        'stockCode': stock_code,
        'action': trade_action_to_str(trade_strategy.action),
        'strategy': str(trade_strategy.strategy)
    }

class RecommendationList(Resource):
    @token_required
    def get(self):
        try:
            date = request.args['date']
            recommendation_stock_list = database_manager.get_recommendation_stock_list()
            return [ stock_code_to_strategy_info(code.stock_code, date) for code in recommendation_stock_list ]
        except Exception as e:
            print(e)
            abort(400, 'missing date')

class UserOperation(Resource):
    @token_required
    def get(self):
        try:
            email = request.args['email']
        except:
            abort(400, 'missing user email')
        user_info = database_manager.get_user_info(email)
        return user_info.to_json() if user_info is not None else None

    def post(self):
        body = request.json
        try:
            user = User(
                email=body['email'],
                username=body['username'],
                password=encrypt_string(body['password']),
                first_name=body.get('first_name', ''),
                last_name=body.get('last_name', '')
            )
            database_manager.add(user)
        except:
            abort(400, 'missing fields for user info')
        return None, 201

class WatchStockOperation(Resource):
    @token_required
    def get(self):
        try:
            user_id = int(request.args['user_id'])
            date = request.args['date']
        except:
            abort(400, 'missing user id')
        watch_list = database_manager.get_user_watch_stock(user_id)
        return [ stock_code_to_strategy_info(code.stock_code, date) for code in watch_list ]

    @token_required
    def post(self):
        try:
            body = request.json
            if not insert_if_not_exist(int(body['user_id']), body['stock_code']):
                raise Exception()
        except Exception as e:
            print(e)
            abort(400)
        return None, 201
    
    @token_required
    def delete(self):
        try:
            body = request.json
            database_manager.delete_user_watch_stock(int(body['user_id']), body['stock_code'])
        except:
            abort(400)
        return None, 204

class BuyStockOperation(Resource):
    @token_required
    def get(self):
        try:
            user_id = int(request.args['user_id'])
            date = request.args['date']
        except:
            abort(400, 'missing user id')
        buy_list = database_manager.get_user_buy_stock(user_id)
        return [ stock_code_to_strategy_info(code.stock_code, date) for code in buy_list ]
    
    @token_required
    def post(self):
        try:
            body = request.json
            database_manager.add_user_buy_stock(int(body['user_id']), body['stock_code'])
        except:
            abort(400)
        return None, 201

    @token_required
    def delete(self):
        try:
            body = request.json
            database_manager.delete_user_buy_stock(int(body['user_id']), body['stock_code'])
        except:
            abort(400)
        return None, 204

class Login(Resource):
    def post(self):
        try:
            body = request.json
            email = body['email']
            password = body['password']
            user = database_manager.get_user_info(email)
            if user is None or encrypt_string(password) != user.password:
                raise Exception()
            token = jwt.encode({
                'email': email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'exp': datetime.utcnow() + timedelta(days=7)
            }, app.config['SECRET_KEY'],  algorithm='HS256')
            return {
                'token': token.decode('utf-8'),
                'id': user.user_id
            }
        except Exception as e:
            print(e)
            abort(400)
    @token_required
    def get(self):
        return True

class Server:
    def __init__(self):
        self._app = Flask(__name__)
        self._api = Api(self._app)
        self.api.add_resource(UserOperation, '/user')
        self.api.add_resource(WatchStockOperation, '/watchstock')
        self.api.add_resource(BuyStockOperation, '/buystock')
        self.api.add_resource(Login, '/login')

    def run(self):
        self._app.run(host='0.0.0.0')

    @property
    def api(self):
        return self._api

    @property
    def app(self):
        return self._app

database_manager = DatabaseManager()
date_model = DateModel()
swing_trade_model = SwingTradeModel()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET_KEY'
cors = CORS(app)
api = Api(app)
api.add_resource(UserOperation, '/user')
api.add_resource(WatchStockOperation, '/watchstock')
api.add_resource(BuyStockOperation, '/buystock')
api.add_resource(Login, '/login')
api.add_resource(RecommendationList, '/recommendation')