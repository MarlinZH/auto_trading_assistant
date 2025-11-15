#!/usr/bin/env python
"""Example: Backtest multiple strategies and compare results."""
import pandas as pd
import numpy as np
from datetime import datetime
import logging

from backtesting import Backtester, BacktestConfig, load_historical_data
from strategies import RSIStrategy, MACDStrategy, MovingAverageCrossoverStrategy
from analytics import PortfolioAnalytics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Compare multiple trading strategies."""
    
    # Configuration
    symbol = 'BTC-USD'
    start_date = '2023-01-01'
    end_date = '2024-01-01'
    initial_capital = 10000
    
    print(f"\nBacktesting {symbol} from {start_date} to {end_date}")
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print("=" * 60)
    
    # Load data
    logger.info("Loading historical data...")
    try:
        data = load_historical_data(symbol, start_date, end_date)
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        logger.info("\nNote: Install yfinance to load data automatically:")
        logger.info("  pip install yfinance")
        return
    
    logger.info(f"Loaded {len(data)} data points")
    
    # Define strategies to test
    strategies = [
        ('RSI', RSIStrategy(rsi_period=14, oversold=30, overbought=70)),
        ('MACD', MACDStrategy(fast_period=12, slow_period=26, signal_period=9)),
        ('MA Crossover', MovingAverageCrossoverStrategy(fast_period=50, slow_period=200)),
    ]
    
    # Backtest configuration
    config = BacktestConfig(
        initial_capital=initial_capital,
        commission=0.001,  # 0.1%
        slippage=0.0005,   # 0.05%
        stop_loss=5.0,     # 5%
        take_profit=10.0,  # 10%
    )
    
    results_summary = []
    
    # Test each strategy
    for name, strategy in strategies:
        print(f"\n\nTesting {name} Strategy")
        print("-" * 60)
        
        # Generate signals
        signals = strategy.generate_signals(data)
        
        # Run backtest
        backtester = Backtester(config)
        results = backtester.run(data, signals)
        
        # Calculate analytics
        returns = results.equity_curve.pct_change().dropna()
        report = PortfolioAnalytics.generate_report(
            results.equity_curve,
            returns,
            results.trades
        )
        
        # Store summary
        results_summary.append({
            'Strategy': name,
            'Total Return': report['total_return'],
            'Annualized Return': report['annualized_return'],
            'Sharpe Ratio': report['sharpe_ratio'],
            'Max Drawdown': report['max_drawdown'],
            'Win Rate': report.get('win_rate', 0),
            'Total Trades': report.get('total_trades', 0),
            'Final Equity': results.equity_curve.iloc[-1]
        })
        
        # Print results
        print(f"\nFinal Equity: ${results.equity_curve.iloc[-1]:,.2f}")
        print(f"Total Return: {report['total_return']:.2f}%")
        print(f"Sharpe Ratio: {report['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {report['max_drawdown']:.2f}%")
        print(f"Total Trades: {report.get('total_trades', 0)}")
        print(f"Win Rate: {report.get('win_rate', 0):.2f}%")
    
    # Compare strategies
    print("\n\n" + "=" * 60)
    print("STRATEGY COMPARISON")
    print("=" * 60)
    
    comparison_df = pd.DataFrame(results_summary)
    comparison_df = comparison_df.sort_values('Total Return', ascending=False)
    
    print("\n" + comparison_df.to_string(index=False))
    
    # Find best strategy
    best_strategy = comparison_df.iloc[0]
    print(f"\n✨ Best Strategy: {best_strategy['Strategy']}")
    print(f"   Total Return: {best_strategy['Total Return']:.2f}%")
    print(f"   Final Equity: ${best_strategy['Final Equity']:,.2f}")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()