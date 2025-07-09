from pydantic import BaseModel, PositiveFloat, PositiveInt, ValidationError

class BotConfig(BaseModel):
    base_order_size: PositiveFloat
    averaging_order_size: PositiveFloat
    max_averaging_orders: PositiveInt
    averaging_order_size_multiplier: PositiveFloat
    price_deviation: PositiveFloat
    averaging_order_step_multiplier: PositiveFloat
    take_profit: PositiveFloat
    reinvest_profit: PositiveFloat

