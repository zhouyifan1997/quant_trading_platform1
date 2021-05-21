from constants.api_constant import (
    POLYGON_API_KEY,
    VINTAGE_API_KEY,
    VINTAGE_URL,
    BASIC_INFO_FIELD_NAME,
    ERROR_MESSAGE,
)
from models.database_model.database_manager_stock_basic_info import StockBasicInfo

import json
import requests
from typing import *

class VintageBasicInfoQueryParams:
    def __init__(self, stock_code: str):
        self._func_name = 'TIME_SERIES_DAILY_ADJUSTED'
        self._stock_code = stock_code
        self._output_size = 'full'
        self._data_type = 'json'
        self._apikey = VINTAGE_API_KEY

    def to_params(self) -> Dict[str, str]:
        return {
            'function': self._func_name,
            'symbol': self._stock_code,
            'outputsize': self._output_size,
            'apikey': self._apikey,
            'datatype': self._data_type
        }

def query_basic_info(stock_code: str) -> Tuple[List[StockBasicInfo], bool]:
    print('Querying basic values for', stock_code)
    basic_info_list: List[StockBasicInfo] = []
    payload = VintageBasicInfoQueryParams(stock_code).to_params()
    response = requests.get(VINTAGE_URL, params=payload)
    response_json = json.loads(response.text)

    if response_json.get('Information') is not None:
        return None, True
    
    values = response_json.get('Time Series (Daily)')
    if values is None:
        return None, False
    for key in values:
        basic_info = values[key]
        curr = StockBasicInfo(
            stock_code=stock_code, 
            stock_info_date=key, 
            open=float(basic_info[BASIC_INFO_FIELD_NAME['open']]),
            close=float(basic_info[BASIC_INFO_FIELD_NAME['close']]),
            high=float(basic_info[BASIC_INFO_FIELD_NAME['high']]),
            low=float(basic_info[BASIC_INFO_FIELD_NAME['low']]),
            volume=float(basic_info[BASIC_INFO_FIELD_NAME['volume']])
        )
        basic_info_list.append(curr)
    return basic_info_list, True