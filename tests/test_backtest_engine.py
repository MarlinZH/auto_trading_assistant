"""Unit tests for BacktestEngine."""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from backtesting import BacktestEngine, DataLoader, TradingStrategies


class TestBacktestEngine:
    """Test suite for BacktestEngine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = BacktestEngine(initial_capital=10000.0, commission=0.001)
        
        # Generate sample data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        self.data = DataLoader.generate_sample_data(
            start=start_date,
            end=end_date,
            initial_price=50000.0,
            volatility=0.01,
            freq='1H'
        )
    
    def test_initialization(self):
        """Test engine initializes correctly."""
        assert self.engine.initial_capital == 10000.0
        assert self.engine.commission == 0.001
        assert self.engine.capital == 10000.0
        assert not self.engine.position.is_open
        assert len(self.engine.trades) == 0
    
    def test_buy_order(self):
        """Test buy order execution."""
        timestamp = datetime.now()
        symbol = 'BTC'
        price = 50000.0
        quantity = 0.1
        
        success = self.engine.buy(timestamp, symbol, price, quantity)
        
        assert success is True
        assert self.engine.position.is_open
        assert self.engine.position.quantity == quantity
        assert self.engine.position.entry_price == price
        assert len(self.engine.trades) == 1
        
        # Check capital deducted
        expected_cost = price * quantity * (1 + self.engine.commission)
        assert self.engine.capital == pytest.approx(10000.0 - expected_cost, rel=1e-5)
    
    def test_sell_order(self):
        """Test sell order execution."""
        timestamp = datetime.now()
        symbol = 'BTC'
        buy_price = 50000.0
        sell_price = 52000.0
        quantity = 0.1
        
        # First buy
        self.engine.buy(timestamp, symbol, buy_price, quantity)
        capital_after_buy = self.engine.capital
        
        # Then sell
        success = self.engine.sell(timestamp, symbol, sell_price, quantity)
        
        assert success is True
        assert not self.engine.position.is_open
        assert len(self.engine.trades) == 2
        
        # Check profit realized
        expected_proceeds = sell_price * quantity * (1 - self.engine.commission)
        assert self.engine.capital == pytest.approx(capital_after_buy + expected_proceeds, rel=1e-5)
    
    def test_insufficient_capital(self):
        """Test buy fails with insufficient capital."""
        timestamp = datetime.now()
        symbol = 'BTC'
        price = 50000.0
        quantity = 10.0  # Way too much
        
        success = self.engine.buy(timestamp, symbol, price, quantity)
        
        assert success is False
        assert not self.engine.position.is_open
        assert len(self.engine.trades) == 0
        assert self.engine.capital == 10000.0  # Unchanged
    
    def test_insufficient_position(self):
        """Test sell fails without position."""
        timestamp = datetime.now()
        symbol = 'BTC'
        price = 50000.0
        quantity = 0.1
        
        success = self.engine.sell(timestamp, symbol, price, quantity)
        
        assert success is False
        assert len(self.engine.trades) == 0
    
    def test_portfolio_value(self):
        """Test portfolio value calculation."""
        timestamp = datetime.now()
        symbol = 'BTC'
        buy_price = 50000.0
        current_price = 52000.0
        quantity = 0.1
        
        # Before any trades
        assert self.engine.get_portfolio_value(current_price) == 10000.0
        
        # After buy
        self.engine.buy(timestamp, symbol, buy_price, quantity)
        portfolio_value = self.engine.get_portfolio_value(current_price)
        
        expected_value = self.engine.capital + (quantity * current_price)
        assert portfolio_value == pytest.approx(expected_value, rel=1e-5)
    
    def test_reset(self):
        """Test engine reset."""
        timestamp = datetime.now()
        self.engine.buy(timestamp, 'BTC', 50000.0, 0.1)
        
        self.engine.reset()
        
        assert self.engine.capital == self.engine.initial_capital
        assert not self.engine.position.is_open
        assert len(self.engine.trades) == 0
        assert len(self.engine.equity_history) == 0
    
    def test_backtest_execution(self):
        """Test full backtest execution."""
        strategy = TradingStrategies.simple_moving_average_crossover(5, 10)
        result = self.engine.run(self.data, strategy)
        
        assert result is not None
        assert result.initial_capital == 10000.0
        assert result.final_capital > 0
        assert result.total_trades >= 0
        assert len(result.equity_curve) == len(self.data)
    
    def test_commission_calculation(self):
        """Test commission is properly calculated."""
        timestamp = datetime.now()
        symbol = 'BTC'
        price = 50000.0
        quantity = 0.1
        
        # Buy
        self.engine.buy(timestamp, symbol, price, quantity)
        buy_trade = self.engine.trades[0]
        
        expected_commission = price * quantity * self.engine.commission
        assert buy_trade.commission == pytest.approx(expected_commission, rel=1e-5)
        
        # Sell
        self.engine.sell(timestamp, symbol, price, quantity)
        sell_trade = self.engine.trades[1]
        
        assert sell_trade.commission == pytest.approx(expected_commission, rel=1e-5)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])