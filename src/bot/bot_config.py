from pydantic import BaseModel, PositiveFloat, PositiveInt, NonNegativeFloat, ValidationError, model_validator
from constants import Asset, Timeframe
from typing_extensions import Self

class BotConfig(BaseModel):
    base_order_size: PositiveFloat
    averaging_order_size: PositiveFloat
    max_averaging_orders: PositiveInt
    averaging_order_size_multiplier: PositiveFloat
    price_deviation: PositiveFloat
    averaging_order_step_multiplier: PositiveFloat
    take_profit: NonNegativeFloat
    reinvest_profit: NonNegativeFloat
    assets: list[Asset]
    timeframes: list[Timeframe]

    @model_validator(mode='after')
    def check_assets(self) -> Self:
        if not self.assets:
            raise ValueError(f"must provide at least one pair for backtesting")
        return self
