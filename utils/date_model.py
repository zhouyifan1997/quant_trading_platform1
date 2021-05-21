from datetime import (
    datetime,
    timedelta,
)
from pytz import timezone
import holidays

us_holidays = holidays.US()

DATE_FORMAT = '%Y-%m-%d'

class DateModel:
    def get_today(self) -> str:
        now = datetime.now(tz=timezone("EST"))
        now_str = now.strftime(DATE_FORMAT)            
        return now_str if now.hour >= 16 else self.get_prev_week_day(now_str)
    
    def get_skip_day(self, date: str, skip_val: int) -> str:
        time = datetime.strptime(date, DATE_FORMAT)
        time += timedelta(days=skip_val)
        return time.strftime(DATE_FORMAT)

    def get_prev_week_day(self, date: str) -> str:
        prev = self.get_skip_day(date, -1)
        while not self.is_valid_trade_day(prev):
            prev = self.get_skip_day(prev, -1)
        return prev

    def get_next_week_day(self, date: str) -> str:
        next = self.get_skip_day(date, 1)
        while not self.is_valid_trade_day(next):
            next = self.get_skip_day(next, 1)
        return next

    def get_year(self, date: str) -> int:
        curr = datetime.strptime(date, DATE_FORMAT).year
        return curr

    def is_valid_trade_day(self, date: str) -> bool:
        return datetime.strptime(date, DATE_FORMAT).weekday() < 5 and \
         date not in us_holidays

    def to_str(self, date: datetime.date) -> str:
        return date.strftime(DATE_FORMAT)
