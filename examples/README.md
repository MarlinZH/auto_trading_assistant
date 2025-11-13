# Examples

This directory contains example scripts demonstrating Phase 2 features.

## Backtesting Examples

### 1. Compare Multiple Strategies

```bash
python examples/backtest_example.py
```

Compares RSI, MACD, and Moving Average Crossover strategies on Bitcoin historical data.

**What it does:**
- Loads BTC-USD data from Yahoo Finance
- Tests 3 different strategies
- Prints performance comparison
- Shows which strategy performed best

### 2. CLI Backtesting

```bash
# Backtest RSI strategy on Bitcoin
python backtest_cli.py --symbol BTC-USD --strategy rsi --start 2023-01-01 --end 2024-01-01

# Backtest MACD on Ethereum with custom parameters
python backtest_cli.py --symbol ETH-USD --strategy macd --start 2023-01-01 --end 2024-01-01 --capital 50000

# List all available strategies
python backtest_cli.py --list-strategies

# Save results to CSV
python backtest_cli.py --symbol AAPL --strategy ma_crossover --start 2023-01-01 --end 2024-01-01 --output results.csv
```

## Live Trading Integration

### 3. Integrate Strategies with Live Bot

```bash
python examples/live_strategy_example.py
```

Shows how to integrate Phase 2 strategies with the existing `trading_bot.py`.

**Integration Steps:**

1. **Import strategy modules** in `trading_bot.py`:
```python
from strategies import MACDStrategy, RSIStrategy
import pandas as pd
```

2. **Add strategy configuration** to `config.py`:
```python
STRATEGY_NAME: str = os.getenv('STRATEGY_NAME', 'macd')
STRATEGY_PARAMS: dict = {}
```

3. **Replace trading logic** in `trading_bot.py`:
```python
def trading_logic(self) -> None:
    # Get recent price history (store last N prices)
    if not hasattr(self, 'price_history'):
        self.price_history = []
    
    current_price = self.get_binance_price(symbol)
    self.price_history.append(current_price)
    
    # Keep last 100 prices
    if len(self.price_history) > 100:
        self.price_history.pop(0)
    
    # Need enough data for indicators
    if len(self.price_history) < 50:
        return
    
    # Create price series
    prices = pd.Series(self.price_history)
    
    # Get strategy signal
    signal = self.get_strategy_signal(prices)
    
    if signal == 1 and not self.current_position:
        self.execute_buy(symbol, quantity, current_price)
    elif signal == -1 and self.current_position:
        self.execute_sell(symbol, quantity, current_price)

def get_strategy_signal(self, prices: pd.Series) -> int:
    data = pd.DataFrame({
        'close': prices,
        'high': prices,
        'low': prices,
        'open': prices,
        'volume': [1] * len(prices)
    })
    
    strategy = MACDStrategy()  # or get_strategy(config.STRATEGY_NAME)
    signals = strategy.generate_signals(data)
    return int(signals.iloc[-1])
```

## Custom Strategy Example

Create your own strategy by extending `BaseStrategy`:

```python
from strategies import BaseStrategy
import pandas as pd

class MyCustomStrategy(BaseStrategy):
    def __init__(self, param1=10, param2=20):
        super().__init__('MyCustom', {'param1': param1, 'param2': param2})
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=data.index)
        
        # Your custom logic here
        # signals[condition] = 1  # Buy
        # signals[other_condition] = -1  # Sell
        
        return signals

# Test it
strategy = MyCustomStrategy(param1=15)
backtester = Backtester()
results = backtester.run(data, strategy.generate_signals(data))
```

## Requirements

For examples to work, install:

```bash
pip install yfinance pandas numpy
```

For plotting:

```bash
pip install matplotlib
```

## Tips

1. **Always backtest first** before using strategies in live trading
2. **Start with paper trading** to verify strategy behavior
3. **Monitor performance** and adjust parameters based on results
4. **Use stop losses** to limit downside risk
5. **Diversify** - don't rely on a single strategy