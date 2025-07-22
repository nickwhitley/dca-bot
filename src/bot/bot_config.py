from pydantic import BaseModel, PositiveFloat, PositiveInt, ValidationError, model_validator
from constants import Asset, Timeframe
from typing_extensions import Self

class BotConfig(BaseModel):
    base_order_size: PositiveFloat
    averaging_order_size: PositiveFloat
    max_averaging_orders: PositiveInt
    averaging_order_size_multiplier: PositiveFloat
    price_deviation: PositiveFloat
    averaging_order_step_multiplier: PositiveFloat
    take_profit: PositiveFloat
    reinvest_profit: PositiveFloat
    pairs: list[Asset]
    timeframes: list[Timeframe]

    @model_validator(mode='after')
    def check_pairs(self) -> Self:
        if not self.pairs:
            raise ValueError(f"must provide at least one pair for backtesting")
        return self
