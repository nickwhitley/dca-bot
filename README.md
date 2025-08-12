# DCA Bot Backtester

A Python-based backtesting tool for a **Dollar Cost Averaging (DCA)** trading strategy.  
This application simulates trades over historical market data, calculates profits, supports dynamic position sizing, and includes optional profit reinvestment for compounding growth.

---

## Features

- **Configurable Bot Settings**  
  Control order sizes, number of averaging orders, price deviation steps, take profit %, and reinvestment % via `BotConfig`.

- **Dynamic Scaling**  
  Automatically adjusts `base_order_size` and `averaging_order_size` to fit your starting balance.

- **Profit Reinvestment**  
  Optionally reinvest a percentage of profits into future trades for compounding.

- **Backtest Over Historical Data**  
  Simulates trades from a given start date to end date using OHLCV market data.

- **Support for Multiple Assets and Timeframes**  
  Easily test different markets and candle intervals.

- **Detailed Reporting**  
  Prints clean summaries for both bot configuration and backtest results.

---

## Requirements

- Python 3.10+
- pandas  
- pydantic  
- loguru  

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Usage

Run backtest with:
```bash
python3 src/main.py <ASSET> <STARTING_BALANCE>
```

Example:
```bash
python3 src/main.py ADA_USD 1000
```

---

## Configuration

Modify defaults in `main.py` or pass through arguments:
- **ASSET**: Must match `Asset` enum value (e.g., `ADA_USD`, `BTC_USD`, `SHIB_USD`)
- **STARTING_BALANCE**: Initial capital for backtest.

Example BotConfig snippet:
```python
bot_config = BotConfig(
    base_order_size=50,
    averaging_order_size=100,
    max_averaging_orders=6,
    averaging_order_size_multiplier=1.28,
    price_deviation=1.5,
    averaging_order_step_multiplier=1.85,
    take_profit=1.5,
    reinvest_profit_pct=0,
    assets=[Asset.ADA_USD],
    timeframes=[Timeframe.H1]
)
```

---

## Output

Example bot configuration printout:
```
BotConfig:
  Base Order Size: 39.57
  Averaging Order Size: 79.14
  Max Averaging Orders: 6
  Averaging Order Size Multiplier: 1.2800
  Price Deviation (%): 1.50
  Averaging Order Step Multiplier: 1.8500
  Take Profit (%): 1.50
  Reinvest Profit (%): 0.00
  Assets: ['ADA_USD']
  Timeframes: ['H1']
  Max Balance for Bot Usage: 991.01
```

Example backtest result:
```
ADA_USD results:
  Starting Balance: 1000.00
  Number of Trades: 484
  Total Profit: 860.37
  Profit %: 86.04%
  Final Balance: 1860.37
```

---