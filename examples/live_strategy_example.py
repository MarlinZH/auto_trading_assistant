#!/usr/bin/env python
"""Example: Integrate Phase 2 strategies with live trading bot."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies import MACDStrategy, RSIStrategy
from indicators import TechnicalIndicators
import pandas as pd
import numpy as np


def get_strategy_signal(prices: pd.Series, strategy_name: str = 'macd') -> int:
    """
    Get trading signal from a strategy.
    
    Args:
        prices: Recent price data (pandas Series with at least 50 points)
        strategy_name: Strategy to use ('macd', 'rsi', etc.)
        
    Returns:
        Signal: 1 (buy), -1 (sell), 0 (hold)
    """
    # Create DataFrame format expected by strategies
    data = pd.DataFrame({
        'close': prices,
        'high': prices,  # Simplified - in real use, get actual high
        'low': prices,   # Simplified - in real use, get actual low
        'open': prices,
        'volume': [1] * len(prices)  # Dummy volume
    })
    
    # Select strategy
    if strategy_name == 'macd':
        strategy = MACDStrategy(fast_period=12, slow_period=26, signal_period=9)
    elif strategy_name == 'rsi':
        strategy = RSIStrategy(rsi_period=14, oversold=30, overbought=70)
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")
    
    # Generate signals
    signals = strategy.generate_signals(data)
    
    # Return most recent signal
    return int(signals.iloc[-1])


def enhanced_trading_logic_example():
    """
    Example of how to integrate Phase 2 strategies with the existing trading bot.
    
    This replaces the simple trading logic in trading_bot.py with strategy-based signals.
    """
    print("Enhanced Trading Logic Example")
    print("="*60)
    
    # Simulate recent price data (in real use, this comes from Binance API)
    np.random.seed(42)
    base_price = 50000
    prices = pd.Series([base_price + np.random.randn() * 1000 for _ in range(100)])
    prices.index = pd.date_range('2024-01-01', periods=len(prices), freq='H')
    
    print(f"\nCurrent Price: ${prices.iloc[-1]:.2f}")
    print(f"Price History: {len(prices)} periods")
    
    # Test multiple strategies
    strategies_to_test = ['macd', 'rsi']
    
    for strategy_name in strategies_to_test:
        signal = get_strategy_signal(prices, strategy_name)
        
        signal_str = "BUY" if signal == 1 else "SELL" if signal == -1 else "HOLD"
        print(f"\n{strategy_name.upper()} Strategy Signal: {signal_str}")
        
        # In trading_bot.py, you would use this signal like:
        # if signal == 1 and not self.current_position:
        #     self.execute_buy(symbol, quantity, current_price)
        # elif signal == -1 and self.current_position:
        #     self.execute_sell(symbol, quantity, current_price)
    
    print("\n" + "="*60)
    print("\nIntegration Steps:")
    print("1. Import strategy modules in trading_bot.py")
    print("2. Replace simple trading_logic() with strategy-based signals")
    print("3. Configure desired strategy in config.py")
    print("4. Use get_strategy_signal() to get trade signals")
    print("5. Backtest before going live!")


if __name__ == '__main__':
    enhanced_trading_logic_example()