#!/usr/bin/env python3
"""Example: Run a backtest with different strategies."""
import sys
sys.path.append('.')

from datetime import datetime, timedelta
import logging

from backtesting import (
    BacktestEngine,
    DataLoader,
    TradingStrategies
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("="*60)
    print("  BACKTESTING EXAMPLE")
    print("="*60)
    
    # 1. Generate sample data
    print("\n[1/4] Loading data...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 1 year
    
    data = DataLoader.generate_sample_data(
        start=start_date,
        end=end_date,
        initial_price=50000.0,
        volatility=0.02,
        freq='1H'
    )
    
    print(f"Loaded {len(data)} bars")
    print(f"Date range: {data.index[0]} to {data.index[-1]}")
    print(f"Price range: ${data['low'].min():.2f} - ${data['high'].max():.2f}")
    
    # 2. Define strategies to test
    strategies = [
        ("SMA Crossover (10/50)", TradingStrategies.simple_moving_average_crossover(10, 50)),
        ("RSI Mean Reversion", TradingStrategies.rsi_mean_reversion(14, 30, 70)),
        ("MACD Crossover", TradingStrategies.macd_crossover(12, 26, 9)),
        ("Bollinger Bounce", TradingStrategies.bollinger_band_bounce(20, 2.0)),
        ("Momentum", TradingStrategies.momentum_strategy(10, 0.02)),
    ]
    
    # 3. Run backtests
    print("\n[2/4] Running backtests...\n")
    results = []
    
    for name, strategy in strategies:
        print(f"\nTesting: {name}")
        print("-" * 60)
        
        engine = BacktestEngine(initial_capital=10000.0, commission=0.001)
        result = engine.run(data, strategy)
        results.append((name, result))
        
        # Quick summary
        print(f"Return: {result.total_return_pct:.2f}%")
        print(f"Trades: {result.total_trades} (Win rate: {result.win_rate:.1f}%)")
        print(f"Sharpe: {result.sharpe_ratio:.2f}")
        print(f"Max DD: {result.max_drawdown_pct:.2f}%")
    
    # 4. Compare strategies
    print("\n[3/4] Strategy Comparison")
    print("="*60)
    print(f"{'Strategy':<30} {'Return %':>10} {'Sharpe':>8} {'Win %':>8} {'Trades':>8}")
    print("-" * 60)
    
    for name, result in results:
        print(f"{name:<30} {result.total_return_pct:>9.2f}% {result.sharpe_ratio:>8.2f} "
              f"{result.win_rate:>7.1f}% {result.total_trades:>8}")
    
    # 5. Best strategy
    print("\n[4/4] Best Strategy Details")
    print("="*60)
    best_strategy = max(results, key=lambda x: x[1].total_return_pct)
    print(f"\nBest performer: {best_strategy[0]}")
    print(best_strategy[1].summary())
    
    print("\n✅ Backtest complete!")
    print("\nTip: Use the visualization module to plot equity curves and analyze results.")

if __name__ == "__main__":
    main()