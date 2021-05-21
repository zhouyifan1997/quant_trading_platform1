from models.database_model.database_manager import (
    DatabaseManager,
    StockBasicInfo,
)
from utils.date_model import DateModel

from enum import Enum

class TradeAction(Enum):
    BUY = 1
    SELL = 2
    PASS = 3

class TradeStrategy:
    def __init__(self, action: TradeAction, strategy: int = 0):
        self._action = action
        self._strategy = strategy
    
    @property
    def action(self) -> TradeAction:
        return self._action

    @property
    def strategy(self) -> float:
        return self._strategy

    def __repr__(self) -> str:
        if self._action == TradeAction.SELL:
            return "Sell"
        if self._action == TradeAction.BUY:
            return "Buy (strategy %d)" % (self._strategy)
        return "Passing"

class SwingTradeModel:
    def __init__(self):
        self._database_manager = DatabaseManager()
        self._date_model = DateModel()

    def _is_swing(self, stock_code: str, date: str) -> bool:
        # Determine if close price is above all ema lines
        assert self._date_model.is_valid_trade_day(date)
        ema_info = self._database_manager.get_stock_ema_info(stock_code, date)
        stock_basic_info = self._database_manager.get_stock_basic_info(stock_code, date)
        assert ema_info
        assert stock_code
        for value in [ema_info.one, ema_info.two, ema_info.three, ema_info.four, ema_info.five]:
            if stock_basic_info.close < value:
                return False
        return True

    def _is_swing_after_non_swing(self, stock_code: str, date: str) -> bool:
        # prev weekday can be Thanksgiving, we need to find prev working weekday
        prev_day = self._date_model.get_prev_week_day(date)
        return not self._is_swing(stock_code, prev_day) and self._is_swing(stock_code, date)

    def _has_stock_info(self, stock_code: str, date: str) -> bool:
        return self._database_manager.get_stock_basic_info(stock_code, date) is not None
    
    def _has_ema_info(self, stock_code: str, date: str) -> bool:
        return self._database_manager.get_stock_ema_info(stock_code, date) is not None
    
    def _is_valid_input(self, stock_code: str, date: str) -> bool:
        return self._has_ema_info(stock_code, date) and self._has_stock_info(stock_code, date)

    def _is_valid_input_for_determine(self, stock_code: str, date: str) -> bool:
        prev_day = self._date_model.get_prev_week_day(date)
        prev_prev_day = self._date_model.get_prev_week_day(prev_day)
        return self._is_valid_input(stock_code, date) and \
            self._is_valid_input(stock_code, prev_day) and \
            self._is_valid_input(stock_code, prev_prev_day)

    def _is_strategy_one(self, stock_code: str, date: str) -> bool:
        return self._is_swing_after_non_swing(stock_code, date)

    def _is_big_sun(self, basic_info: StockBasicInfo) -> bool:
        def get_percent_change(one, two):
            return (two - one) / one
        day_range_percent = get_percent_change(basic_info.open, basic_info.close)
        day_range = basic_info.close - basic_info.open
        max_min_day_range = basic_info.high - basic_info.low
        return  day_range_percent >= 0.05 and max_min_day_range * 0.5 < day_range

    def _is_rise_with_large_volume(self, stock_code: str, date: str) -> bool:
        prev_day = self._date_model.get_prev_week_day(date)
        prev_basic_info = self._database_manager.get_stock_basic_info(stock_code, prev_day)
        curr_basic_info = self._database_manager.get_stock_basic_info(stock_code, date)
        return self._is_big_sun(curr_basic_info) and prev_basic_info.volume * 2 <= curr_basic_info.volume

    def _is_pullback_with_small_volume(self, stock_code: str, date: str) -> bool:
        prev_day = self._date_model.get_prev_week_day(date)
        prev_basic_info = self._database_manager.get_stock_basic_info(stock_code, prev_day)
        curr_basic_info = self._database_manager.get_stock_basic_info(stock_code, date)
        return curr_basic_info.volume <= prev_basic_info.volume * 0.8

    def _is_strategy_two(self, stock_code: str, date: str) -> bool:
        # 带量上涨后的缩量回调
        prev_day = self._date_model.get_prev_week_day(date)
        return self._is_rise_with_large_volume(stock_code, prev_day) and self._is_pullback_with_small_volume(stock_code, date)

    def determine_strategy(self, stock_code: str, date: str) -> TradeStrategy:
        # If we don't have data on either date or prev trade day, pass
        if not self._is_valid_input_for_determine(stock_code, date):
            return TradeStrategy(TradeAction.PASS)
        if not self._is_swing(stock_code, date):
            # Sell the stock when the price drops down below ema lines
            return TradeStrategy(
                TradeAction.SELL,
                0,
            )
        if self._is_strategy_one(stock_code, date):
            # If is long array (多头排列), buy
            return TradeStrategy(
                TradeAction.BUY,
                1,
            )
    
        if self._is_strategy_two(stock_code, date):
            return TradeStrategy(
                TradeAction.BUY,
                2,
            )
        
        return TradeStrategy(TradeAction.PASS)
