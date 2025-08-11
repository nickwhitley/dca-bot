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
    reinvest_profit_pct: NonNegativeFloat
    assets: list[Asset]
    timeframes: list[Timeframe]
    
    @property
    def max_balance_for_bot_usage(self) -> float:
        total = self.base_order_size
        total += sum(
            round(self.averaging_order_size * (self.averaging_order_size_multiplier ** i), 2)
            for i in range(self.max_averaging_orders)
        )
        return total
    

    @model_validator(mode='after')
    def check_assets(self) -> Self:
        if not self.assets:
            raise ValueError(f"must provide at least one pair for backtesting")
        return self
    
    def reinvest_profit(self, profit: float):
        if self.reinvest_profit_pct <= 0:
            return
        
        profit_to_reinvest = profit * (self.reinvest_profit_pct / 100.0)
        growth_factor = (self.max_balance_for_bot_usage + profit_to_reinvest) / self.max_balance_for_bot_usage

        self.base_order_size *= growth_factor
        self.averaging_order_size *= growth_factor

        self.base_order_size = round(self.base_order_size, 2)
        self.averaging_order_size = round(self.averaging_order_size, 2)
    
    

#     def __str__(self):
#         return f"""

# """
