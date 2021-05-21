from constants.api_constant import (
    POLYGON_API_KEY,
    VINTAGE_API_KEY,
    VINTAGE_URL,
    EMA_QUERY_PERIOD_OLD_STOCK,
    ERROR_MESSAGE,
)
from models.database_model.database_manager_stock_ema_info import StockEMAInfo

import json
import requests
from typing import *

class VintageEMAQueryParams:
    def __init__(self, stock_code: str, time_period: int):
        self._func_name = 'EMA'
        self._stock_code = stock_code
        self._time_period = time_period
        self._interval = 'daily'
        self._data_type = 'json'
        self._apikey = VINTAGE_API_KEY
        self._series_type = 'close'

    def to_params(self) -> Dict[str, Union[str, int]]:
        return {
            'function': self._func_name,
            'symbol': self._stock_code,
            'interval': self._interval,
            'time_period': self._time_period,
            'series_type': self._series_type,
            'apikey': self._apikey,
            'datatype': self._data_type
        }
    
def query_ema_values(stock_code: str) -> Tuple[List[StockEMAInfo], bool]:
    print('Querying ema values for', stock_code)
    ema_dict: Dict[str, List[float]] = {}
    ema_list: List[StockEMAInfo] = []
    for time_period in EMA_QUERY_PERIOD_OLD_STOCK:
        payload = VintageEMAQueryParams(stock_code, time_period).to_params()
        response = requests.get(VINTAGE_URL, params=payload)
        response_json = json.loads(response.text)
        
        if response_json.get("Information") is not None:
            return None, True
        
        values = response_json.get('Technical Analysis: EMA')
        if values is None or len(values) == 0:
            return None, False
        
        for key in values:
            if ema_dict.get(key) is None:
                ema_dict[key] = [float(values[key]["EMA"])]
            else:
                ema_dict[key].append(float(values[key]["EMA"]))

    for date in ema_dict:
        ema_values = ema_dict[date]
        if len(ema_values) < 5:
            continue
        one, two, three, four, five = ema_values
        curr = StockEMAInfo(
            stock_code=stock_code,
            stock_info_date=date, 
            one=one,
            two=two, 
            three=three, 
            four=four, 
            five=five
        )
        ema_list.append(curr)

    return ema_list, True