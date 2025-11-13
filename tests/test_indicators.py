"""Unit tests for technical indicators."""
import pytest
import pandas as pd
import numpy as np
from indicators import TechnicalIndicators, SignalGenerator


class TestTechnicalIndicators:
    """Test technical indicator calculations."""
    
    def setup_method(self):
        """Set up test data."""
        # Create sample price data
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        prices = pd.Series(
            100 + np.cumsum(np.random.randn(100)),
            index=dates
        )
        self.data = pd.DataFrame({
            'close': prices,
            'high': prices * 1.01,
            'low': prices * 0.99,
            'volume': np.random.randint(1000, 10000, 100)
        })
    
    def test_sma(self):
        """Test Simple Moving Average calculation."""
        sma = TechnicalIndicators.sma(self.data['close'], period=20)
        
        assert len(sma) == len(self.data)
        assert not sma.iloc[-1] != sma.iloc[-1]  # Check not NaN
        assert sma.iloc[0] != sma.iloc[0]  # First value should be NaN
    
    def test_ema(self):
        """Test Exponential Moving Average calculation."""
        ema = TechnicalIndicators.ema(self.data['close'], period=20)
        
        assert len(ema) == len(self.data)
        assert not ema.iloc[-1] != ema.iloc[-1]  # Check not NaN
    
    def test_rsi(self):
        """Test RSI calculation."""
        rsi = TechnicalIndicators.rsi(self.data['close'], period=14)
        
        assert len(rsi) == len(self.data)
        # RSI should be between 0 and 100
        valid_rsi = rsi.dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()
    
    def test_macd(self):
        """Test MACD calculation."""
        macd_line, signal_line, histogram = TechnicalIndicators.macd(
            self.data['close'],
            fast_period=12,
            slow_period=26,
            signal_period=9
        )
        
        assert len(macd_line) == len(self.data)
        assert len(signal_line) == len(self.data)
        assert len(histogram) == len(self.data)
        
        # Histogram should equal MACD - Signal
        valid_idx = ~histogram.isna()
        np.testing.assert_array_almost_equal(
            histogram[valid_idx],
            (macd_line - signal_line)[valid_idx]
        )
    
    def test_bollinger_bands(self):
        """Test Bollinger Bands calculation."""
        upper, middle, lower = TechnicalIndicators.bollinger_bands(
            self.data['close'],
            period=20,
            num_std=2.0
        )
        
        assert len(upper) == len(self.data)
        assert len(middle) == len(self.data)
        assert len(lower) == len(self.data)
        
        # Upper should be > Middle > Lower
        valid_idx = ~upper.isna()
        assert (upper[valid_idx] >= middle[valid_idx]).all()
        assert (middle[valid_idx] >= lower[valid_idx]).all()
    
    def test_atr(self):
        """Test Average True Range calculation."""
        atr = TechnicalIndicators.atr(
            self.data['high'],
            self.data['low'],
            self.data['close'],
            period=14
        )
        
        assert len(atr) == len(self.data)
        # ATR should be positive
        valid_atr = atr.dropna()
        assert (valid_atr >= 0).all()


class TestSignalGenerator:
    """Test signal generation from indicators."""
    
    def setup_method(self):
        """Set up test data."""
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        self.index = dates
    
    def test_rsi_signals(self):
        """Test RSI signal generation."""
        # Create RSI values
        rsi = pd.Series([25, 30, 35, 65, 70, 75], index=self.index[:6])
        
        signals = SignalGenerator.rsi_signals(rsi, oversold=30, overbought=70)
        
        # First value (25) should generate buy signal
        assert signals.iloc[0] == 1
        # Last value (75) should generate sell signal
        assert signals.iloc[-1] == -1
    
    def test_macd_signals(self):
        """Test MACD crossover signals."""
        # Create crossover scenario
        macd_line = pd.Series([1, 2, 3], index=self.index[:3])
        signal_line = pd.Series([2, 2, 2], index=self.index[:3])
        
        signals = SignalGenerator.macd_signals(macd_line, signal_line)
        
        # Bullish crossover at index 1 (MACD crosses above signal)
        assert signals.iloc[1] == 1
    
    def test_moving_average_crossover(self):
        """Test MA crossover signals."""
        fast_ma = pd.Series([100, 102, 104], index=self.index[:3])
        slow_ma = pd.Series([103, 103, 103], index=self.index[:3])
        
        signals = SignalGenerator.moving_average_crossover(fast_ma, slow_ma)
        
        # Golden cross at index 1
        assert signals.iloc[1] == 1
    
    def test_combine_signals(self):
        """Test signal combination."""
        signal1 = pd.Series([1, 1, 0, -1], index=self.index[:4])
        signal2 = pd.Series([1, 0, -1, -1], index=self.index[:4])
        signal3 = pd.Series([0, 1, -1, -1], index=self.index[:4])
        
        combined = SignalGenerator.combine_signals(
            signal1, signal2, signal3,
            threshold=2
        )
        
        # First value: 2 buys, 1 hold -> buy signal
        assert combined.iloc[0] == 1
        # Last value: 3 sells -> sell signal
        assert combined.iloc[3] == -1
        # Second value: 2 buys, 1 hold -> buy signal
        assert combined.iloc[1] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])