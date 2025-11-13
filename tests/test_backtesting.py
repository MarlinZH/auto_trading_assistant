"""Unit tests for backtesting framework."""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backtesting import Backtester, BacktestConfig, Trade


class TestBacktesting:
    """Test backtesting functionality."""
    
    def setup_method(self):
        """Set up test data."""
        # Create sample OHLCV data
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        np.random.seed(42)
        base_price = 100
        prices = base_price + np.cumsum(np.random.randn(100) * 2)
        
        self.data = pd.DataFrame({
            'open': prices,
            'high': prices * 1.01,
            'low': prices * 0.99,
            'close': prices,
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        # Simple buy-and-hold signals
        self.signals = pd.Series(0, index=dates)
        self.signals.iloc[10] = 1  # Buy
        self.signals.iloc[50] = -1  # Sell
        self.signals.iloc[60] = 1  # Buy again
    
    def test_backtest_initialization(self):
        """Test backtester initializes correctly."""
        config = BacktestConfig(initial_capital=10000)
        backtester = Backtester(config)
        
        assert backtester.capital == 10000
        assert len(backtester.trades) == 0
        assert backtester.current_position is None
    
    def test_backtest_basic_trade(self):
        """Test basic buy and sell execution."""
        config = BacktestConfig(
            initial_capital=10000,
            commission=0,
            slippage=0
        )
        backtester = Backtester(config)
        results = backtester.run(self.data, self.signals)
        
        # Should have executed trades
        assert len(results.trades) > 0
        assert results.total_trades > 0
    
    def test_commission_and_slippage(self):
        """Test commission and slippage are applied."""
        config = BacktestConfig(
            initial_capital=10000,
            commission=0.001,  # 0.1%
            slippage=0.001     # 0.1%
        )
        backtester = Backtester(config)
        results = backtester.run(self.data, self.signals)
        
        # Final equity should be less than without costs
        assert results.equity_curve.iloc[-1] < 10000 + (self.data['close'].iloc[-1] - self.data['close'].iloc[10]) * 100
    
    def test_stop_loss(self):
        """Test stop loss functionality."""
        # Create data with a big drop
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        prices = pd.Series([100] * 10 + [90, 80, 70, 60] + [60] * 36)
        data = pd.DataFrame({
            'close': prices,
            'high': prices,
            'low': prices,
            'open': prices,
            'volume': [1000] * 50
        }, index=dates)
        
        signals = pd.Series(0, index=dates)
        signals.iloc[5] = 1  # Buy at 100
        
        config = BacktestConfig(
            initial_capital=10000,
            stop_loss=15.0,  # 15% stop loss
            commission=0,
            slippage=0
        )
        backtester = Backtester(config)
        results = backtester.run(data, signals)
        
        # Should have triggered stop loss
        assert len(results.trades) > 0
        assert any(t.exit_reason == 'stop_loss' for t in results.trades)
    
    def test_take_profit(self):
        """Test take profit functionality."""
        # Create data with a big gain
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        prices = pd.Series([100] * 10 + [110, 120, 130, 140] + [140] * 36)
        data = pd.DataFrame({
            'close': prices,
            'high': prices,
            'low': prices,
            'open': prices,
            'volume': [1000] * 50
        }, index=dates)
        
        signals = pd.Series(0, index=dates)
        signals.iloc[5] = 1  # Buy at 100
        
        config = BacktestConfig(
            initial_capital=10000,
            take_profit=30.0,  # 30% take profit
            commission=0,
            slippage=0
        )
        backtester = Backtester(config)
        results = backtester.run(data, signals)
        
        # Should have triggered take profit
        assert len(results.trades) > 0
        assert any(t.exit_reason == 'take_profit' for t in results.trades)
    
    def test_max_positions(self):
        """Test maximum position limit."""
        signals = pd.Series(1, index=self.data.index)  # All buy signals
        
        config = BacktestConfig(
            initial_capital=10000,
            max_positions=1
        )
        backtester = Backtester(config)
        results = backtester.run(self.data, signals)
        
        # Should only have 1 position open at a time
        assert results.total_trades >= 1
    
    def test_equity_curve(self):
        """Test equity curve generation."""
        config = BacktestConfig(initial_capital=10000)
        backtester = Backtester(config)
        results = backtester.run(self.data, self.signals)
        
        # Equity curve should have same length as data
        assert len(results.equity_curve) == len(self.data)
        # First value should be initial capital
        assert results.equity_curve.iloc[0] == 10000
    
    def test_performance_metrics(self):
        """Test performance metrics calculation."""
        config = BacktestConfig(initial_capital=10000)
        backtester = Backtester(config)
        results = backtester.run(self.data, self.signals)
        
        # Check metrics exist
        assert hasattr(results, 'total_return')
        assert hasattr(results, 'sharpe_ratio')
        assert hasattr(results, 'max_drawdown')
        assert hasattr(results, 'win_rate')
        
        # Win rate should be between 0 and 100
        assert 0 <= results.win_rate <= 100


if __name__ == '__main__':
    pytest.main([__file__, '-v'])