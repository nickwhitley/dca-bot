from pydantic import BaseModel, ValidationError, AfterValidator, model_validator
from datetime import datetime
from typing import Annotated
from typing_extensions import Self
from constants import Timeframe
from bot.bot_config import BotConfig

class BacktestConfig(BaseModel):
    start_date: datetime
    end_date: datetime

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
    
    # @model_validator(mode='after')
    # def check_timeframes(self) -> Self:
    #     for timeframe