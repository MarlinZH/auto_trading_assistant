#!/usr/bin/env python
"""Command-line interface for backtesting trading strategies."""
import argparse
import pandas as pd
import sys
import logging
from datetime import datetime

from backtesting import Backtester, BacktestConfig, load_historical_data
from strategies import get_strategy, STRATEGY_REGISTRY
from analytics import PortfolioAnalytics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Backtest trading strategies on historical data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Backtest RSI strategy on BTC
  python backtest_cli.py --symbol BTC-USD --strategy rsi --start 2023-01-01 --end 2024-01-01
  
  # Backtest MACD strategy with custom capital
  python backtest_cli.py --symbol ETH-USD --strategy macd --capital 50000 --commission 0.002
  
  # Backtest with stop loss and take profit
  python backtest_cli.py --symbol AAPL --strategy ma_crossover --stop-loss 5 --take-profit 10
  
  # List available strategies
  python backtest_cli.py --list-strategies
        """
    )
    
    # Data arguments
    parser.add_argument('--symbol', type=str, help='Trading symbol (e.g., BTC-USD, AAPL)')
    parser.add_argument('--start', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--data-source', type=str, default='yfinance',
                       choices=['yfinance', 'csv'], help='Data source')
    parser.add_argument('--csv-file', type=str, help='Path to CSV file (if using csv source)')
    
    # Strategy arguments
    parser.add_argument('--strategy', type=str, help=f'Strategy to use. Available: {", ".join(STRATEGY_REGISTRY.keys())}')
    parser.add_argument('--list-strategies', action='store_true', help='List available strategies')
    
    # Backtest configuration
    parser.add_argument('--capital', type=float, default=10000, help='Initial capital')
    parser.add_argument('--commission', type=float, default=0.001, help='Commission rate (0.001 = 0.1%%)')
    parser.add_argument('--slippage', type=float, default=0.0005, help='Slippage rate')
    parser.add_argument('--position-size', type=float, default=1.0, help='Position size as fraction of capital (0-1)')
    parser.add_argument('--stop-loss', type=float, help='Stop loss percentage')
    parser.add_argument('--take-profit', type=float, help='Take profit percentage')
    
    # Strategy-specific parameters
    parser.add_argument('--rsi-period', type=int, default=14, help='RSI period')
    parser.add_argument('--rsi-oversold', type=float, default=30, help='RSI oversold level')
    parser.add_argument('--rsi-overbought', type=float, default=70, help='RSI overbought level')
    parser.add_argument('--fast-period', type=int, default=12, help='Fast MA/MACD period')
    parser.add_argument('--slow-period', type=int, default=26, help='Slow MA/MACD period')
    parser.add_argument('--signal-period', type=int, default=9, help='MACD signal period')
    parser.add_argument('--ma-type', type=str, default='sma', choices=['sma', 'ema'], help='Moving average type')
    
    # Output options
    parser.add_argument('--output', type=str, help='Save results to CSV file')
    parser.add_argument('--plot', action='store_true', help='Generate plots (requires matplotlib)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # List strategies
    if args.list_strategies:
        print("\nAvailable Strategies:")
        print("="*50)
        for name, strategy_class in STRATEGY_REGISTRY.items():
            print(f"  {name:20} - {strategy_class.__doc__ or 'No description'}")
        print("="*50)
        return 0
    
    # Validate required arguments
    if not args.symbol or not args.start or not args.end or not args.strategy:
        parser.error("--symbol, --start, --end, and --strategy are required (or use --list-strategies)")
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Load data
        logger.info(f"Loading {args.symbol} data from {args.start} to {args.end}...")
        
        if args.data_source == 'csv':
            if not args.csv_file:
                parser.error("--csv-file required when using csv data source")
            data = pd.read_csv(args.csv_file, index_col=0, parse_dates=True)
        else:
            data = load_historical_data(args.symbol, args.start, args.end, source=args.data_source)
        
        if data.empty:
            logger.error("No data loaded. Check symbol and date range.")
            return 1
        
        logger.info(f"Loaded {len(data)} data points")
        
        # Create strategy
        logger.info(f"Initializing {args.strategy} strategy...")
        
        strategy_params = {}
        if args.strategy == 'rsi':
            strategy_params = {
                'rsi_period': args.rsi_period,
                'oversold': args.rsi_oversold,
                'overbought': args.rsi_overbought
            }
        elif args.strategy == 'macd':
            strategy_params = {
                'fast_period': args.fast_period,
                'slow_period': args.slow_period,
                'signal_period': args.signal_period
            }
        elif args.strategy == 'ma_crossover':
            strategy_params = {
                'fast_period': args.fast_period,
                'slow_period': args.slow_period,
                'ma_type': args.ma_type
            }
        
        strategy = get_strategy(args.strategy, **strategy_params)
        signals = strategy.generate_signals(data)
        
        # Configure backtester
        config = BacktestConfig(
            initial_capital=args.capital,
            commission=args.commission,
            slippage=args.slippage,
            position_size=args.position_size,
            stop_loss=args.stop_loss,
            take_profit=args.take_profit
        )
        
        # Run backtest
        logger.info("Running backtest...")
        backtester = Backtester(config)
        results = backtester.run(data, signals)
        
        # Print results
        print(results)
        
        # Generate analytics report
        returns = results.equity_curve.pct_change().dropna()
        report = PortfolioAnalytics.generate_report(
            results.equity_curve,
            returns,
            results.trades
        )
        PortfolioAnalytics.print_report(report)
        
        # Save results
        if args.output:
            logger.info(f"Saving results to {args.output}...")
            results.equity_curve.to_csv(args.output)
            logger.info("Results saved")
        
        # Plot results
        if args.plot:
            try:
                import matplotlib.pyplot as plt
                
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
                
                # Price and signals
                ax1.plot(data.index, data['close'], label='Price', alpha=0.7)
                buy_signals = signals[signals == 1]
                sell_signals = signals[signals == -1]
                ax1.scatter(buy_signals.index, data.loc[buy_signals.index, 'close'],
                           marker='^', color='g', s=100, label='Buy')
                ax1.scatter(sell_signals.index, data.loc[sell_signals.index, 'close'],
                           marker='v', color='r', s=100, label='Sell')
                ax1.set_title(f"{args.symbol} - {strategy.name} Strategy")
                ax1.set_ylabel('Price')
                ax1.legend()
                ax1.grid(True, alpha=0.3)
                
                # Equity curve
                ax2.plot(results.equity_curve.index, results.equity_curve.values, label='Equity')
                ax2.axhline(y=config.initial_capital, color='gray', linestyle='--', alpha=0.5, label='Initial Capital')
                ax2.set_title('Equity Curve')
                ax2.set_ylabel('Equity ($)')
                ax2.set_xlabel('Date')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
                
                plt.tight_layout()
                
                plot_file = args.output.replace('.csv', '.png') if args.output else 'backtest_results.png'
                plt.savefig(plot_file, dpi=150)
                logger.info(f"Plot saved to {plot_file}")
                plt.show()
                
            except ImportError:
                logger.warning("matplotlib not installed. Install with: pip install matplotlib")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during backtest: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())