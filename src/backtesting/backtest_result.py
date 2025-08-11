from pydantic import BaseModel
from constants import Asset
from models.trade import Trade

class BacktestResult(BaseModel):
    asset: Asset
    trades: list[Trade]
    ending_balance: float
    gain_loss: float
    percent_gain_loss: float

    def __str__(self):
        return f"""
{self.asset} results:
Number of trades: {len(self.trades)}
Total Profit: {self.gain_loss}
Profit %: {self.percent_gain_loss}%
Final Balance: {self.ending_balance}
"""