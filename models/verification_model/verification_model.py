from models.database_model.database_manager import *
from models.swing_trade_model.swing_trade_model import *
from utils.date_model import DateModel

import csv
import threading
from typing import *

class PositionInfo:
    def __init__(self, stock_code: str) -> None:
        self._init_balance = 5000
        self._current_strategy = 0
        self._balance_last_year = 5000
        self._balance_last_weekday = 5000
        self._balance_last_op = 5000
        self._success_op_count = 0
        self._total_op_count = 0
        self._stock_code = stock_code
        self._ticker_balance = self._init_balance
        self._position = 0
        self._one_after_two_count = 0
        self._two_after_one_count = 0

    @property
    def stock_code(self) -> str:
        return self._stock_code

    @property
    def balance_last_weekday(self) -> float:
        return self._balance_last_weekday

    @property
    def success_op_count(self) -> int:
        return self._success_op_count
    
    @property
    def total_op_count(self) -> int:
        return self._total_op_count

    @property
    def current_strategy(self) -> int:
        return self._current_strategy

    @property
    def one_after_two_count(self) -> int:
        return self._one_after_two_count

    @property
    def two_after_one_count(self) -> int:
        return self._two_after_one_count
    
    @property
    def position(self) -> float:
        return self._position

    @current_strategy.setter
    def current_strategy(self, current_strategy) -> None:
        self._current_strategy = current_strategy

    @one_after_two_count.setter
    def one_after_two_count(self, one_after_two_count) -> None:
        self._one_after_two_count = one_after_two_count

    @two_after_one_count.setter
    def two_after_one_count(self, two_after_one_count) -> None:
        self._two_after_one_count = two_after_one_count

    def update_balance_last_year(self) -> None:
        self._balance_last_year = self._balance_last_weekday

    def update_balance_last_weekday(self, price: float) -> None:
        self._balance_last_weekday = self.get_value(price)

    def get_value(self, price: float) -> float:
        return self._ticker_balance + self._position * price

    def get_profit_rate_all_time(self, value: float) -> float:
        return (value - self._init_balance) / self._init_balance * 100

    def get_profit_rate_one_year(self, value: float) -> float:
        return (value - self._balance_last_year) / self._balance_last_year * 100

    def buy(self, price: float, percent: float) -> None:
        available = self._ticker_balance * percent / 100
        self._position += available / price
        self._ticker_balance -= available
    
    def sell(self, price: float, percent: float) -> None:
        stock_count = self._position * percent / 100
        self._ticker_balance += stock_count * price
        self._position -= stock_count
        if stock_count > 0:
            self._total_op_count += 1
        if self._ticker_balance > self._balance_last_op:
            self._success_op_count += 1
        self._balance_last_op = self._ticker_balance

    def get_summary_last_weekday(self) -> (str, str, str):
        value = self.balance_last_weekday
        profit_rate_all_time = self.get_profit_rate_all_time(value)
        profit_rate_one_year = self.get_profit_rate_one_year(value)
        value_str = "%.2f" % value
        profit_rate_all_time_str = "" if profit_rate_all_time > -10 else "(Warning)"
        profit_rate_all_time_str += "%.2f" % profit_rate_all_time
        profit_rate_one_year_str = "" if profit_rate_one_year > -10 else "(Warning)"
        profit_rate_one_year_str += "%.2f" % profit_rate_one_year
        return (value_str, profit_rate_all_time_str, profit_rate_one_year_str)

    def get_summary(self, price: float) -> (str, str, str):
        value = self.get_value(price)
        profit_rate_all_time = self.get_profit_rate_all_time(value)
        profit_rate_one_year = self.get_profit_rate_one_year(value)
        value_str = "%.2f" % value
        profit_rate_all_time_str = "" if profit_rate_all_time > -10 else "(Warning)"
        profit_rate_all_time_str += "%.2f" % profit_rate_all_time
        profit_rate_one_year_str = "" if profit_rate_one_year > -10 else "(Warning)"
        profit_rate_one_year_str += "%.2f" % profit_rate_one_year
        return (value_str, profit_rate_all_time_str, profit_rate_one_year_str)

    def get_success_rate(self) -> float:
        return self._success_op_count / self._total_op_count if self._total_op_count > 0 else 0

class VerificationModel:
    def __init__(self):
        self._database_manager = DatabaseManager.get_instance()
        self._swing_trade_model = SwingTradeModel()
        self._date_model = DateModel()
        self._start_date = self._date_model.get_next_week_day('2018-01-01')
        self._curr_year = self._date_model.get_year(self._start_date)
        self._end_date = '2020-12-31'
        self._position_info_list: List[PositionInfo] = []
        verification_stock_list: List[str] = self._database_manager.get_recommendation_stock_list()
        self._summary_field: List[str] = ['Date']
        self._summary_values: List[List[str]] = []
        for stock in verification_stock_list:
            if self._database_manager.is_valid_verification_stock(stock.stock_code, self._start_date):
                self._position_info_list.append(PositionInfo(stock.stock_code))
                self._summary_field.append(stock.stock_code)
                self._summary_field.append(stock.stock_code + "Profit Rate All Time")
                self._summary_field.append(stock.stock_code + "Profit Rate One Year")
        self._summary_field.append("Buy")
        self._summary_field.append("Sell")
        self._summary_field.append("Total")
        self._summary_field.append("Total Profit Rate All Time")
        self._summary_field.append("Total Profit Rate One Year")
        self._initial_value = self.get_total_value(self._start_date)
        self._prev_value = self._initial_value

    def _update_prev_value(self, total_value: float) -> None:
        self._prev_value = total_value

    def get_profit_rate_all_time(self, total_value: float) -> float:
        return (total_value - self._initial_value) / self._initial_value * 100

    def get_profit_rate_one_year(self, total_value: float) -> float:
        return (total_value - self._prev_value) / self._prev_value * 100

    def get_total_value(self, date: str):
        total = 0
        for position_info in self._position_info_list:
            basicInfo = self._database_manager.get_stock_basic_info(position_info.stock_code, date)
            if basicInfo is None:
                total += position_info.balance_last_weekday
            else:
                price = basicInfo.close
                total += position_info.get_value(price)
        return total

    def get_summary(self, curr: str) -> Tuple[str, str, str]:
        total_value = self.get_total_value(curr)
        profit_rate_all_time = self.get_profit_rate_all_time(total_value)
        profit_rate_one_year = self.get_profit_rate_one_year(total_value)
        total_value_str = "%.2f" % total_value
        profit_rate_all_time_str = "" if profit_rate_all_time > -10 else "(Warning)"
        profit_rate_all_time_str += "%.2f" % profit_rate_all_time
        profit_rate_one_year_str = "" if profit_rate_one_year > -10 else "(Warning)"
        profit_rate_one_year_str += "%.2f" % profit_rate_one_year
        return (total_value_str, profit_rate_all_time_str, profit_rate_one_year_str)

    def run_test(self):
        curr = self._start_date
        while curr < self._end_date:
            curr_year = self._date_model.get_year(curr)
            if curr_year != self._curr_year:
                self._curr_year = curr_year
                last_trade_day = self._date_model.get_prev_week_day(curr)
                self._prev_value = self.get_total_value(last_trade_day)
                for position_info in self._position_info_list:
                    position_info.update_balance_last_year()
            curr_summary_values: List[str] = [curr]
            buy_count = 0
            sell_count = 0
            for position_info in self._position_info_list:
                strategy = self._swing_trade_model.determine_strategy(position_info.stock_code, curr)
                action = strategy.action
                strategy_number = strategy.strategy
                basic_info = self._database_manager.get_stock_basic_info(position_info.stock_code, curr)
                
                if basic_info is None:
                    value, profit_rate_all_time, profit_rate_one_year = position_info.get_summary_last_weekday()
                    curr_summary_values.append(value)
                    curr_summary_values.append(profit_rate_all_time)
                    curr_summary_values.append(profit_rate_one_year)
                    continue
                position_info.update_balance_last_weekday(basic_info.close)
                price = basic_info.close
                if action == TradeAction.BUY:
                    if position_info.position > 0 and position_info.current_strategy != strategy_number:
                        if strategy_number == 1:
                            position_info.one_after_two_count += 1
                        else:
                            position_info.two_after_one_count += 1
                    else:
                        position_info.current_strategy = strategy_number
                    position_info.buy(price, 100)
                    buy_count += 1
                if action == TradeAction.SELL:
                    position_info.current_strategy = 0
                    position_info.sell(price, 100)
                    sell_count += 1
                value, profit_rate_all_time, profit_rate_one_year = position_info.get_summary(price)
                curr_summary_values.append(value)
                curr_summary_values.append(profit_rate_all_time)
                curr_summary_values.append(profit_rate_one_year)
            curr = self._date_model.get_next_week_day(curr)
            curr_summary_values.append(buy_count)
            curr_summary_values.append(sell_count)
            total, total_profit_rate_all_time, total_profit_rate_one_year = self.get_summary(curr)
            curr_summary_values.append(total)
            curr_summary_values.append(total_profit_rate_all_time)
            curr_summary_values.append(total_profit_rate_one_year)
            self._summary_values.append(curr_summary_values)
            print(curr, total)
        
        self._summary_values.append([])

        success_op_count = 0
        total_op_count = 0

        for position_info in self._position_info_list:
            success_op_count += position_info.success_op_count
            total_op_count += position_info.total_op_count
            self._summary_values.append([position_info.stock_code, position_info.get_success_rate(), position_info.two_after_one_count, position_info.one_after_two_count])

        self._summary_values.append(['TOTAL', success_op_count / total_op_count if total_op_count > 0 else 0])

        self.write_to_file()
    
    def write_to_file(self) -> None:
        with open('summary/策略1+策略2.csv', 'w') as f: 
            # using csv.writer method from CSV package 
            write = csv.writer(f) 
            write.writerow(self._summary_field) 
            write.writerows(self._summary_values)