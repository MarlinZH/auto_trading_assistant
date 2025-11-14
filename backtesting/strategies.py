"""Pre-built trading strategies for backtesting."""
import pandas as pd
import numpy as np
from typing import TYPE_CHECKING
from backtesting.indicators import TechnicalIndicators as ta

if TYPE_CHECKING:
    from backtesting.backtest_engine import BacktestEngine


class TradingStrategies:
    """Collection of pre-built trading strategies."""
    
    @staticmethod
    def simple_moving_average_crossover(short_period: int = 10, long_period: int = 50):
        """
        Simple Moving Average Crossover Strategy.
        
        Buy when short MA crosses above long MA.
        Sell when short MA crosses below long MA.
        
        Args:
            short_period: Fast MA period
            long_period: Slow MA period
            
        Returns:
            Strategy function
        """
        def strategy(data: pd.DataFrame, index: int, engine: 'BacktestEngine'):
            if index < long_period:
                return
            
            # Calculate MAs
            close = data['close']
            short_ma = ta.sma(close, short_period)
            long_ma = ta.sma(close, long_period)
            
            current_short = short_ma.iloc[index]
            current_long = long_ma.iloc[index]
            prev_short = short_ma.iloc[index - 1]
            prev_long = long_ma.iloc[index - 1]
            
            symbol = 'BTC'
            quantity = 0.001
            current_price = data['close'].iloc[index]
            timestamp = data.index[index]
            
            # Buy signal: short MA crosses above long MA
            if prev_short <= prev_long and current_short > current_long:
                if not engine.position.is_open:
                    engine.buy(timestamp, symbol, current_price, quantity)
            
            # Sell signal: short MA crosses below long MA
            elif prev_short >= prev_long and current_short < current_long:
                if engine.position.is_open:
                    engine.sell(timestamp, symbol, current_price, quantity)
        
        return strategy
    
    @staticmethod
    def rsi_mean_reversion(period: int = 14, oversold: float = 30, overbought: float = 70):
        """
        RSI Mean Reversion Strategy.
        
        Buy when RSI crosses above oversold level.
        Sell when RSI crosses below overbought level.
        
        Args:
            period: RSI period
            oversold: Oversold threshold
            overbought: Overbought threshold
            
        Returns:
            Strategy function
        """
        def strategy(data: pd.DataFrame, index: int, engine: 'BacktestEngine'):
            if index < period + 1:
                return
            
            # Calculate RSI
            close = data['close']
            rsi = ta.rsi(close, period)
            
            current_rsi = rsi.iloc[index]
            prev_rsi = rsi.iloc[index - 1]
            
            symbol = 'BTC'
            quantity = 0.001
            current_price = data['close'].iloc[index]
            timestamp = data.index[index]
            
            # Buy signal: RSI crosses above oversold
            if prev_rsi <= oversold and current_rsi > oversold:
                if not engine.position.is_open:
                    engine.buy(timestamp, symbol, current_price, quantity)
            
            # Sell signal: RSI crosses below overbought
            elif prev_rsi >= overbought and current_rsi < overbought:
                if engine.position.is_open:
                    engine.sell(timestamp, symbol, current_price, quantity)
        
        return strategy
    
    @staticmethod
    def macd_crossover(fast: int = 12, slow: int = 26, signal: int = 9):
        """
        MACD Crossover Strategy.
        
        Buy when MACD crosses above signal line.
        Sell when MACD crosses below signal line.
        
        Args:
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
            
        Returns:
            Strategy function
        """
        def strategy(data: pd.DataFrame, index: int, engine: 'BacktestEngine'):
            if index < slow + signal:
                return
            
            # Calculate MACD
            close = data['close']
            macd_line, signal_line, histogram = ta.macd(close, fast, slow, signal)
            
            current_macd = macd_line.iloc[index]
            current_signal = signal_line.iloc[index]
            prev_macd = macd_line.iloc[index - 1]
            prev_signal = signal_line.iloc[index - 1]
            
            symbol = 'BTC'
            quantity = 0.001
            current_price = data['close'].iloc[index]
            timestamp = data.index[index]
            
            # Buy signal: MACD crosses above signal
            if prev_macd <= prev_signal and current_macd > current_signal:
                if not engine.position.is_open:
                    engine.buy(timestamp, symbol, current_price, quantity)
            
            # Sell signal: MACD crosses below signal
            elif prev_macd >= prev_signal and current_macd < current_signal:
                if engine.position.is_open:
                    engine.sell(timestamp, symbol, current_price, quantity)
        
        return strategy
    
    @staticmethod
    def bollinger_band_bounce(period: int = 20, std_dev: float = 2.0):
        """
        Bollinger Band Bounce Strategy.
        
        Buy when price touches lower band.
        Sell when price touches upper band.
        
        Args:
            period: MA period
            std_dev: Standard deviations
            
        Returns:
            Strategy function
        """
        def strategy(data: pd.DataFrame, index: int, engine: 'BacktestEngine'):
            if index < period:
                return
            
            # Calculate Bollinger Bands
            close = data['close']
            upper, middle, lower = ta.bollinger_bands(close, period, std_dev)
            
            current_price = data['close'].iloc[index]
            current_upper = upper.iloc[index]
            current_lower = lower.iloc[index]
            
            symbol = 'BTC'
            quantity = 0.001
            timestamp = data.index[index]
            
            # Buy signal: price at or below lower band
            if current_price <= current_lower:
                if not engine.position.is_open:
                    engine.buy(timestamp, symbol, current_price, quantity)
            
            # Sell signal: price at or above upper band
            elif current_price >= current_upper:
                if engine.position.is_open:
                    engine.sell(timestamp, symbol, current_price, quantity)
        
        return strategy
    
    @staticmethod
    def momentum_strategy(period: int = 10, threshold: float = 0.02):
        """
        Momentum Strategy.
        
        Buy when price momentum is positive and above threshold.
        Sell when momentum turns negative.
        
        Args:
            period: Momentum lookback period
            threshold: Minimum momentum to trigger buy
            
        Returns:
            Strategy function
        """
        def strategy(data: pd.DataFrame, index: int, engine: 'BacktestEngine'):
            if index < period:
                return
            
            # Calculate momentum
            close = data['close']
            current_price = close.iloc[index]
            past_price = close.iloc[index - period]
            momentum = (current_price - past_price) / past_price
            
            symbol = 'BTC'
            quantity = 0.001
            timestamp = data.index[index]
            
            # Buy signal: positive momentum above threshold
            if momentum > threshold:
                if not engine.position.is_open:
                    engine.buy(timestamp, symbol, current_price, quantity)
            
            # Sell signal: negative momentum
            elif momentum < 0:
                if engine.position.is_open:
                    engine.sell(timestamp, symbol, current_price, quantity)
        
        return strategy
    
    @staticmethod
    def trend_following(short_ma: int = 20, long_ma: int = 50, atr_period: int = 14, atr_multiplier: float = 2.0):
        """
        Trend Following with ATR-based stops.
        
        Buy when short MA > long MA and price > short MA.
        Sell when stop loss hit or trend reverses.
        
        Args:
            short_ma: Short MA period
            long_ma: Long MA period
            atr_period: ATR period for stops
            atr_multiplier: ATR multiplier for stop distance
            
        Returns:
            Strategy function
        """
        def strategy(data: pd.DataFrame, index: int, engine: 'BacktestEngine'):
            if index < max(long_ma, atr_period):
                return
            
            # Calculate indicators
            close = data['close']
            short = ta.sma(close, short_ma)
            long = ta.sma(close, long_ma)
            atr = ta.atr(data['high'], data['low'], data['close'], atr_period)
            
            current_price = data['close'].iloc[index]
            current_short = short.iloc[index]
            current_long = long.iloc[index]
            current_atr = atr.iloc[index]
            
            symbol = 'BTC'
            quantity = 0.001
            timestamp = data.index[index]
            
            # Buy signal: uptrend confirmed
            if current_short > current_long and current_price > current_short:
                if not engine.position.is_open:
                    engine.buy(timestamp, symbol, current_price, quantity)
            
            # Sell signal: stop loss or trend reversal
            if engine.position.is_open:
                entry_price = engine.position.entry_price
                stop_loss = entry_price - (current_atr * atr_multiplier)
                
                if current_price < stop_loss or current_short < current_long:
                    engine.sell(timestamp, symbol, current_price, quantity)
        
        return strategy