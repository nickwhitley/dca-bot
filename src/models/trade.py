from pydantic import BaseModel, PositiveFloat
from datetime import datetime
from typing import Optional
from constants import Asset

class Trade(BaseModel):
    asset: Asset
    entry_datetime: datetime
    entry_price: PositiveFloat
    close_datetime: Optional[datetime] = None
    close_price: Optional[PositiveFloat] = None
    base_quantity: Optional[PositiveFloat] = None
    total_quantity: Optional[PositiveFloat] = None
    profit_loss: float = 0
    avg_orders_prices: list[float] = []
    avg_orders_quantities: list[float] = []
    avg_orders_filled: int = 0