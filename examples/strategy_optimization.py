#!/usr/bin/env python3
"""Example: Optimize strategy parameters."""
import sys
sys.path.append('.')

from datetime import datetime, timedelta
import logging
import pandas as pd

from backtesting import (
    BacktestEngine,
    DataLoader,
    TradingStrategies
)

logging.basicConfig(level=logging.WARNING)  # Reduce noise during optimization

def main():
    print("="*60)
    print("  STRATEGY PARAMETER OPTIMIZATION")
    print("="*60)
    
    # Load data
    print("\nLoading data...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)  # 6 months
    
    data = DataLoader.generate_sample_data(
        start=start_date,
        end=end_date,
        initial_price=50000.0,
        volatility=0.02,
        freq='1H'
    )
    
    # Parameter ranges to test
    print("\nOptimizing SMA Crossover parameters...")
    short_periods = range(5, 25, 5)
    long_periods = range(30, 100, 10)
    
    results = []
    total_tests = len(short_periods) * len(long_periods)
    current = 0
    
    for short in short_periods:
        for long in long_periods:
            if short >= long:
                continue
            
            current += 1
            print(f"\rTesting {current}/{total_tests}: Short={short}, Long={long}   ", end='')
            
            strategy = TradingStrategies.simple_moving_average_crossover(short, long)
            engine = BacktestEngine(initial_capital=10000.0, commission=0.001)
            result = engine.run(data, strategy)
            
            results.append({
                'short_period': short,
                'long_period': long,
                'return_pct': result.total_return_pct,
                'sharpe_ratio': result.sharpe_ratio,
                'max_drawdown_pct': result.max_drawdown_pct,
                'win_rate': result.win_rate,
                'total_trades': result.total_trades
            })
    
    # Analyze results
    df = pd.DataFrame(results)
    df.sort_values('return_pct', ascending=False, inplace=True)
    
    print("\n\nTop 10 Parameter Combinations")
    print("="*80)
    print(df.head(10).to_string(index=False))
    
    print("\n\nBest Parameters:")
    best = df.iloc[0]
    print(f"Short Period: {best['short_period']}")
    print(f"Long Period: {best['long_period']}")
    print(f"Return: {best['return_pct']:.2f}%")
    print(f"Sharpe Ratio: {best['sharpe_ratio']:.2f}")
    print(f"Win Rate: {best['win_rate']:.1f}%")
    print(f"Max Drawdown: {best['max_drawdown_pct']:.2f}%")
    
    print("\n⚠️  Warning: Optimized parameters may be overfit to historical data!")
    print("Always validate on out-of-sample data.")

if __name__ == "__main__":
    main()