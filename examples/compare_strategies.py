#!/usr/bin/env python3
"""Example: Compare multiple strategies side-by-side."""
import sys
sys.path.append('.')

from datetime import datetime, timedelta
import logging

from backtesting import (
    BacktestEngine,
    DataLoader,
    TradingStrategies
)

logging.basicConfig(level=logging.WARNING)

def main():
    print("="*80)
    print("  STRATEGY COMPARISON: 1-Year Backtest")
    print("="*80)
    
    # Load data
    print("\nLoading 1 year of hourly data...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    data = DataLoader.generate_sample_data(
        start=start_date,
        end=end_date,
        initial_price=50000.0,
        volatility=0.02,
        freq='1H'
    )
    
    print(f"Data: {len(data)} bars from {data.index[0].date()} to {data.index[-1].date()}")
    
    # Define strategies
    strategies = [
        ("Buy & Hold", lambda data, i, engine: buy_and_hold(data, i, engine)),
        ("SMA 10/50", TradingStrategies.simple_moving_average_crossover(10, 50)),
        ("SMA 20/100", TradingStrategies.simple_moving_average_crossover(20, 100)),
        ("RSI 14", TradingStrategies.rsi_mean_reversion(14, 30, 70)),
        ("MACD", TradingStrategies.macd_crossover(12, 26, 9)),
        ("BB Bounce", TradingStrategies.bollinger_band_bounce(20, 2.0)),
        ("Momentum", TradingStrategies.momentum_strategy(10, 0.02)),
        ("Trend Follow", TradingStrategies.trend_following(20, 50, 14, 2.0)),
    ]
    
    # Run backtests
    print("\nRunning backtests...")
    results = []
    
    for i, (name, strategy) in enumerate(strategies, 1):
        print(f"[{i}/{len(strategies)}] Testing {name}...")
        engine = BacktestEngine(initial_capital=10000.0, commission=0.001)
        result = engine.run(data, strategy)
        results.append((name, result))
    
    # Display comparison table
    print("\n" + "="*120)
    print("STRATEGY COMPARISON")
    print("="*120)
    print(f"{'Strategy':<15} {'Return %':>10} {'Sharpe':>8} {'Max DD %':>10} "
          f"{'Win %':>8} {'Trades':>8} {'Profit Factor':>14}")
    print("-"*120)
    
    for name, result in results:
        print(f"{name:<15} {result.total_return_pct:>9.2f}% {result.sharpe_ratio:>8.2f} "
              f"{result.max_drawdown_pct:>9.2f}% {result.win_rate:>7.1f}% "
              f"{result.total_trades:>8} {result.profit_factor:>14.2f}")
    
    # Rankings
    print("\n" + "="*80)
    print("RANKINGS")
    print("="*80)
    
    print("\nBy Return:")
    sorted_by_return = sorted(results, key=lambda x: x[1].total_return_pct, reverse=True)
    for i, (name, result) in enumerate(sorted_by_return[:3], 1):
        print(f"  {i}. {name:<15} {result.total_return_pct:>7.2f}%")
    
    print("\nBy Sharpe Ratio:")
    sorted_by_sharpe = sorted(results, key=lambda x: x[1].sharpe_ratio, reverse=True)
    for i, (name, result) in enumerate(sorted_by_sharpe[:3], 1):
        print(f"  {i}. {name:<15} {result.sharpe_ratio:>7.2f}")
    
    print("\nBy Win Rate:")
    sorted_by_winrate = sorted(results, key=lambda x: x[1].win_rate, reverse=True)
    for i, (name, result) in enumerate(sorted_by_winrate[:3], 1):
        print(f"  {i}. {name:<15} {result.win_rate:>6.1f}%")
    
    print("\n✅ Analysis complete!")

def buy_and_hold(data, index, engine):
    """Simple buy and hold strategy."""
    if index == 50:  # Buy after initial period
        if not engine.position.is_open:
            engine.buy(data.index[index], 'BTC', data['close'].iloc[index], 0.001)

if __name__ == "__main__":
    main()