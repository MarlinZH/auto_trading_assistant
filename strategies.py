"""Trading strategy implementations."""
import pandas as pd
import numpy as np
from typing import Dict, Optional
from abc import ABC, abstractmethod
import logging

from indicators import TechnicalIndicators, SignalGenerator

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """Base class for trading strategies."""
    
    def __init__(self, name: str, params: Dict = None):
        """Initialize strategy.
        
        Args:
            name: Strategy name
            params: Strategy parameters
        """
        self.name = name
        self.params = params or {}
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate trading signals from price data.
        
        Args:
            data: OHLCV DataFrame with DatetimeIndex
            
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.name} Strategy"


class RSIStrategy(BaseStrategy):
    """RSI-based mean reversion strategy."""
    
    def __init__(self, 
                 rsi_period: int = 14,
                 oversold: float = 30,
                 overbought: float = 70):
        """Initialize RSI strategy.
        
        Args:
            rsi_period: RSI calculation period
            oversold: Oversold threshold
            overbought: Overbought threshold
        """
        params = {
            'rsi_period': rsi_period,
            'oversold': oversold,
            'overbought': overbought
        }
        super().__init__('RSI', params)
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on RSI levels."""
        close = data['close']
        
        # Calculate RSI
        rsi = TechnicalIndicators.rsi(close, self.params['rsi_period'])
        
        # Generate signals
        signals = SignalGenerator.rsi_signals(
            rsi, 
            self.params['oversold'],
            self.params['overbought']
        )
        
        logger.info(f"RSI Strategy: Generated {len(signals[signals != 0])} signals")
        return signals


class MACDStrategy(BaseStrategy):
    """MACD crossover strategy."""
    
    def __init__(self,
                 fast_period: int = 12,
                 slow_period: int = 26,
                 signal_period: int = 9):
        """Initialize MACD strategy.
        
        Args:
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line period
        """
        params = {
            'fast_period': fast_period,
            'slow_period': slow_period,
            'signal_period': signal_period
        }
        super().__init__('MACD', params)
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on MACD crossover."""
        close = data['close']
        
        # Calculate MACD
        macd_line, signal_line, _ = TechnicalIndicators.macd(
            close,
            self.params['fast_period'],
            self.params['slow_period'],
            self.params['signal_period']
        )
        
        # Generate signals
        signals = SignalGenerator.macd_signals(macd_line, signal_line)
        
        logger.info(f"MACD Strategy: Generated {len(signals[signals != 0])} signals")
        return signals


class MovingAverageCrossoverStrategy(BaseStrategy):
    """Moving average crossover strategy."""
    
    def __init__(self,
                 fast_period: int = 50,
                 slow_period: int = 200,
                 ma_type: str = 'sma'):
        """Initialize MA crossover strategy.
        
        Args:
            fast_period: Fast MA period
            slow_period: Slow MA period
            ma_type: Type of MA ('sma' or 'ema')
        """
        params = {
            'fast_period': fast_period,
            'slow_period': slow_period,
            'ma_type': ma_type
        }
        super().__init__('MA_Crossover', params)
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on MA crossover."""
        close = data['close']
        
        # Calculate moving averages
        if self.params['ma_type'] == 'ema':
            fast_ma = TechnicalIndicators.ema(close, self.params['fast_period'])
            slow_ma = TechnicalIndicators.ema(close, self.params['slow_period'])
        else:
            fast_ma = TechnicalIndicators.sma(close, self.params['fast_period'])
            slow_ma = TechnicalIndicators.sma(close, self.params['slow_period'])
        
        # Generate signals
        signals = SignalGenerator.moving_average_crossover(fast_ma, slow_ma)
        
        logger.info(f"MA Crossover Strategy: Generated {len(signals[signals != 0])} signals")
        return signals


class BollingerBandStrategy(BaseStrategy):
    """Bollinger Band mean reversion strategy."""
    
    def __init__(self,
                 period: int = 20,
                 num_std: float = 2.0):
        """Initialize Bollinger Band strategy.
        
        Args:
            period: Moving average period
            num_std: Number of standard deviations
        """
        params = {
            'period': period,
            'num_std': num_std
        }
        super().__init__('Bollinger_Bands', params)
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on Bollinger Band touches."""
        close = data['close']
        
        # Calculate Bollinger Bands
        upper, middle, lower = TechnicalIndicators.bollinger_bands(
            close,
            self.params['period'],
            self.params['num_std']
        )
        
        # Generate signals
        signals = SignalGenerator.bollinger_band_signals(close, upper, lower)
        
        logger.info(f"Bollinger Band Strategy: Generated {len(signals[signals != 0])} signals")
        return signals


class ComboStrategy(BaseStrategy):
    """Combination of multiple strategies."""
    
    def __init__(self, 
                 strategies: list,
                 threshold: int = 2):
        """Initialize combo strategy.
        
        Args:
            strategies: List of strategy instances
            threshold: Minimum agreeing strategies for signal
        """
        params = {
            'strategies': [s.name for s in strategies],
            'threshold': threshold
        }
        super().__init__('Combo', params)
        self.strategies = strategies
        self.threshold = threshold
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate combined signals from multiple strategies."""
        # Get signals from all strategies
        all_signals = [strategy.generate_signals(data) for strategy in self.strategies]
        
        # Combine signals
        combined = SignalGenerator.combine_signals(*all_signals, threshold=self.threshold)
        
        logger.info(f"Combo Strategy: Generated {len(combined[combined != 0])} signals")
        logger.info(f"  Using {len(self.strategies)} strategies with threshold {self.threshold}")
        return combined


class MomentumStrategy(BaseStrategy):
    """Momentum-based trend following strategy."""
    
    def __init__(self,
                 rsi_period: int = 14,
                 macd_fast: int = 12,
                 macd_slow: int = 26,
                 macd_signal: int = 9,
                 adx_period: int = 14,
                 adx_threshold: float = 25):
        """Initialize momentum strategy.
        
        Args:
            rsi_period: RSI period
            macd_fast: MACD fast period
            macd_slow: MACD slow period
            macd_signal: MACD signal period
            adx_period: ADX period
            adx_threshold: Minimum ADX for trend confirmation
        """
        params = {
            'rsi_period': rsi_period,
            'macd_fast': macd_fast,
            'macd_slow': macd_slow,
            'macd_signal': macd_signal,
            'adx_period': adx_period,
            'adx_threshold': adx_threshold
        }
        super().__init__('Momentum', params)
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on momentum indicators."""
        close = data['close']
        high = data['high']
        low = data['low']
        
        # Calculate indicators
        rsi = TechnicalIndicators.rsi(close, self.params['rsi_period'])
        macd_line, signal_line, _ = TechnicalIndicators.macd(
            close,
            self.params['macd_fast'],
            self.params['macd_slow'],
            self.params['macd_signal']
        )
        adx = TechnicalIndicators.adx(
            high, low, close,
            self.params['adx_period']
        )
        
        # Initialize signals
        signals = pd.Series(0, index=data.index)
        
        # Buy conditions:
        # 1. RSI > 50 (bullish momentum)
        # 2. MACD > Signal (bullish)
        # 3. ADX > threshold (strong trend)
        buy_condition = (
            (rsi > 50) &
            (macd_line > signal_line) &
            (adx > self.params['adx_threshold'])
        )
        
        # Sell conditions:
        # 1. RSI < 50 (bearish momentum)
        # 2. MACD < Signal (bearish)
        # 3. ADX > threshold (strong trend)
        sell_condition = (
            (rsi < 50) &
            (macd_line < signal_line) &
            (adx > self.params['adx_threshold'])
        )
        
        signals[buy_condition] = 1
        signals[sell_condition] = -1
        
        logger.info(f"Momentum Strategy: Generated {len(signals[signals != 0])} signals")
        return signals


class MeanReversionStrategy(BaseStrategy):
    """Mean reversion strategy using multiple indicators."""
    
    def __init__(self,
                 rsi_period: int = 14,
                 rsi_oversold: float = 30,
                 rsi_overbought: float = 70,
                 bb_period: int = 20,
                 bb_std: float = 2.0):
        """Initialize mean reversion strategy.
        
        Args:
            rsi_period: RSI period
            rsi_oversold: RSI oversold level
            rsi_overbought: RSI overbought level
            bb_period: Bollinger Band period
            bb_std: Bollinger Band standard deviations
        """
        params = {
            'rsi_period': rsi_period,
            'rsi_oversold': rsi_oversold,
            'rsi_overbought': rsi_overbought,
            'bb_period': bb_period,
            'bb_std': bb_std
        }
        super().__init__('Mean_Reversion', params)
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals for mean reversion."""
        close = data['close']
        
        # Calculate indicators
        rsi = TechnicalIndicators.rsi(close, self.params['rsi_period'])
        upper, middle, lower = TechnicalIndicators.bollinger_bands(
            close,
            self.params['bb_period'],
            self.params['bb_std']
        )
        
        # Initialize signals
        signals = pd.Series(0, index=data.index)
        
        # Buy when both RSI and BB suggest oversold
        buy_condition = (
            (rsi < self.params['rsi_oversold']) &
            (close <= lower)
        )
        
        # Sell when both RSI and BB suggest overbought
        sell_condition = (
            (rsi > self.params['rsi_overbought']) &
            (close >= upper)
        )
        
        signals[buy_condition] = 1
        signals[sell_condition] = -1
        
        logger.info(f"Mean Reversion Strategy: Generated {len(signals[signals != 0])} signals")
        return signals


class BreakoutStrategy(BaseStrategy):
    """Price breakout strategy."""
    
    def __init__(self,
                 lookback_period: int = 20,
                 volume_multiplier: float = 1.5):
        """Initialize breakout strategy.
        
        Args:
            lookback_period: Period for high/low calculation
            volume_multiplier: Volume must exceed this multiple of average
        """
        params = {
            'lookback_period': lookback_period,
            'volume_multiplier': volume_multiplier
        }
        super().__init__('Breakout', params)
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals for breakouts."""
        close = data['close']
        high = data['high']
        low = data['low']
        volume = data.get('volume', pd.Series(1, index=data.index))
        
        # Calculate rolling high/low
        rolling_high = high.rolling(window=self.params['lookback_period']).max()
        rolling_low = low.rolling(window=self.params['lookback_period']).min()
        
        # Calculate average volume
        avg_volume = volume.rolling(window=self.params['lookback_period']).mean()
        
        # Initialize signals
        signals = pd.Series(0, index=data.index)
        
        # Buy on upside breakout with volume confirmation
        buy_condition = (
            (close > rolling_high.shift(1)) &
            (volume > avg_volume * self.params['volume_multiplier'])
        )
        
        # Sell on downside breakdown with volume confirmation
        sell_condition = (
            (close < rolling_low.shift(1)) &
            (volume > avg_volume * self.params['volume_multiplier'])
        )
        
        signals[buy_condition] = 1
        signals[sell_condition] = -1
        
        logger.info(f"Breakout Strategy: Generated {len(signals[signals != 0])} signals")
        return signals


# Strategy factory
STRATEGY_REGISTRY = {
    'rsi': RSIStrategy,
    'macd': MACDStrategy,
    'ma_crossover': MovingAverageCrossoverStrategy,
    'bollinger': BollingerBandStrategy,
    'momentum': MomentumStrategy,
    'mean_reversion': MeanReversionStrategy,
    'breakout': BreakoutStrategy,
}


def get_strategy(name: str, **kwargs) -> BaseStrategy:
    """Factory function to get strategy by name.
    
    Args:
        name: Strategy name
        **kwargs: Strategy parameters
        
    Returns:
        Strategy instance
        
    Example:
        >>> strategy = get_strategy('rsi', rsi_period=14, oversold=30)
    """
    if name not in STRATEGY_REGISTRY:
        raise ValueError(f"Unknown strategy: {name}. Available: {list(STRATEGY_REGISTRY.keys())}")
    
    return STRATEGY_REGISTRY[name](**kwargs)