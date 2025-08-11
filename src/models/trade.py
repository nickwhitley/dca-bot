from pydantic import BaseModel, NonNegativeFloat, PositiveFloat
from datetime import datetime
from typing import Optional
from constants import Asset

class Trade(BaseModel):
    asset: Asset
    entry_datetime: datetime
    entry_price: PositiveFloat
    close_datetime: Optional[datetime] = None
    close_price: NonNegativeFloat = 0
    base_order_size: Optional[PositiveFloat] = None
    total_order_size: Optional[PositiveFloat] = None
    profit_loss: float = 0
    take_profit_levels: list[float] = []
    avg_orders_prices: list[float] = []
    avg_orders_sizes: list[float] = []
    avg_orders_filled: int = 0
    avg_entry_price: float = 0

    def __str__(self):
        return f"""
Trade:
Asset: {self.asset}
Entry Datetime: {self.entry_datetime}
Entry Price: {self.entry_price}
Close Datetime: {self.close_datetime}
Close Price: {self.close_price}
Base Order Size: {self.base_order_size}
Total Size: {self.total_order_size}
Profit Loss: {self.profit_loss}
Take Profit Levels: {[round(x, 5) for x in self.take_profit_levels]}
Averaging Orders Prices: {self.avg_orders_prices}
Averaging Orders Sizes: {self.avg_orders_sizes}
Averaging Orders Filled: {self.avg_orders_filled}
Average Entry Price: {self.avg_entry_price}
"""