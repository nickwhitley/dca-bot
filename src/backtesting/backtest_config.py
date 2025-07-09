from pydantic import BaseModel, ValidationError, AfterValidator, model_validator
from datetime import datetime
from typing import Annotated
from typing_extensions import Self
from constants import Timeframe

available_pairs = [
    "ADA/USD",
]

class BacktestConfig(BaseModel):
    start_date: datetime
    end_date: datetime
    pairs: list[str]
    timeframes: list[Timeframe]

    @model_validator(mode='after')
    def check_start_date(self) -> Self:
        min_date = datetime(2020,1,1)
        if self.start_date < min_date:
            raise ValueError(f'{self.start_date} is less earliest date of: {min_date}')
        return self
    
    @model_validator(mode='after')
    def check_end_date(self) -> Self:
        max_date = datetime.now()
        if self.end_date > max_date:
            raise ValueError(f'{self.end_date} is less earliest date of: {max_date}')
        return self

    @model_validator(mode='after')
    def check_pairs(self) -> Self:
        if self.pairs == [""]:
            raise ValueError(f"must provide at least one pair for backtesting")
        for pair in self.pairs:
            if pair not in available_pairs:
                raise ValueError(f'{pair} not available for backtesting')
        return self
    
    # @model_validator(mode='after')
    # def check_timeframes(self) -> Self:
    #     for timeframe