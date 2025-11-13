"""Technical indicators for trading strategies."""
import pandas as pd
import numpy as np
from typing import Tuple, Optional


class TechnicalIndicators:
    """Calculate common technical indicators for trading analysis."""
    
    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average.
        
        Args:
            data: Price data series
            period: Number of periods for calculation
            
        Returns:
            Series with SMA values
        """
        return data.rolling(window=period).mean()
    
    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average.
        
        Args:
            data: Price data series
            period: Number of periods for calculation
            
        Returns:
            Series with EMA values
        """
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index.
        
        Args:
            data: Price data series
            period: RSI period (default 14)
            
        Returns:
            Series with RSI values (0-100)
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def macd(data: pd.Series, 
             fast_period: int = 12, 
             slow_period: int = 26, 
             signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            data: Price data series
            fast_period: Fast EMA period (default 12)
            slow_period: Slow EMA period (default 26)
            signal_period: Signal line period (default 9)
            
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        fast_ema = TechnicalIndicators.ema(data, fast_period)
        slow_ema = TechnicalIndicators.ema(data, slow_period)
        
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(data: pd.Series, 
                       period: int = 20, 
                       num_std: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands.
        
        Args:
            data: Price data series
            period: Moving average period (default 20)
            num_std: Number of standard deviations (default 2.0)
            
        Returns:
            Tuple of (Upper band, Middle band, Lower band)
        """
        middle_band = TechnicalIndicators.sma(data, period)
        std = data.rolling(window=period).std()
        
        upper_band = middle_band + (std * num_std)
        lower_band = middle_band - (std * num_std)
        
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range (volatility indicator).
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: ATR period (default 14)
            
        Returns:
            Series with ATR values
        """
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def stochastic(high: pd.Series, 
                   low: pd.Series, 
                   close: pd.Series, 
                   period: int = 14) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator.
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: Lookback period (default 14)
            
        Returns:
            Tuple of (%K line, %D line)
        """
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        
        k_line = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_line = k_line.rolling(window=3).mean()
        
        return k_line, d_line
    
    @staticmethod
    def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate On-Balance Volume.
        
        Args:
            close: Close price series
            volume: Volume series
            
        Returns:
            Series with OBV values
        """
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv
    
    @staticmethod
    def adx(high: pd.Series, 
            low: pd.Series, 
            close: pd.Series, 
            period: int = 14) -> pd.Series:
        """Calculate Average Directional Index (trend strength).
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: ADX period (default 14)
            
        Returns:
            Series with ADX values
        """
        # Calculate True Range
        tr = TechnicalIndicators.atr(high, low, close, period=1)
        
        # Calculate directional movement
        up_move = high.diff()
        down_move = -low.diff()
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        plus_dm = pd.Series(plus_dm, index=high.index)
        minus_dm = pd.Series(minus_dm, index=high.index)
        
        # Smooth the values
        tr_smooth = tr.rolling(window=period).sum()
        plus_dm_smooth = plus_dm.rolling(window=period).sum()
        minus_dm_smooth = minus_dm.rolling(window=period).sum()
        
        # Calculate directional indicators
        plus_di = 100 * (plus_dm_smooth / tr_smooth)
        minus_di = 100 * (minus_dm_smooth / tr_smooth)
        
        # Calculate ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    @staticmethod
    def vwap(high: pd.Series, 
             low: pd.Series, 
             close: pd.Series, 
             volume: pd.Series) -> pd.Series:
        """Calculate Volume Weighted Average Price.
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            volume: Volume series
            
        Returns:
            Series with VWAP values
        """
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        
        return vwap


class SignalGenerator:
    """Generate trading signals based on technical indicators."""
    
    @staticmethod
    def rsi_signals(rsi: pd.Series, 
                    oversold: float = 30, 
                    overbought: float = 70) -> pd.Series:
        """Generate buy/sell signals from RSI.
        
        Args:
            rsi: RSI values
            oversold: Oversold threshold (default 30)
            overbought: Overbought threshold (default 70)
            
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        signals = pd.Series(0, index=rsi.index)
        signals[rsi < oversold] = 1  # Buy signal
        signals[rsi > overbought] = -1  # Sell signal
        
        return signals
    
    @staticmethod
    def macd_signals(macd_line: pd.Series, signal_line: pd.Series) -> pd.Series:
        """Generate buy/sell signals from MACD crossover.
        
        Args:
            macd_line: MACD line
            signal_line: Signal line
            
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        signals = pd.Series(0, index=macd_line.index)
        
        # Bullish crossover (MACD crosses above signal)
        signals[(macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))] = 1
        
        # Bearish crossover (MACD crosses below signal)
        signals[(macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))] = -1
        
        return signals
    
    @staticmethod
    def moving_average_crossover(fast_ma: pd.Series, slow_ma: pd.Series) -> pd.Series:
        """Generate signals from moving average crossover.
        
        Args:
            fast_ma: Fast moving average
            slow_ma: Slow moving average
            
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        signals = pd.Series(0, index=fast_ma.index)
        
        # Golden cross (fast MA crosses above slow MA)
        signals[(fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))] = 1
        
        # Death cross (fast MA crosses below slow MA)
        signals[(fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))] = -1
        
        return signals
    
    @staticmethod
    def bollinger_band_signals(close: pd.Series, 
                              upper_band: pd.Series, 
                              lower_band: pd.Series) -> pd.Series:
        """Generate signals from Bollinger Band touches.
        
        Args:
            close: Close price series
            upper_band: Upper Bollinger Band
            lower_band: Lower Bollinger Band
            
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        signals = pd.Series(0, index=close.index)
        
        # Buy when price touches lower band
        signals[close <= lower_band] = 1
        
        # Sell when price touches upper band
        signals[close >= upper_band] = -1
        
        return signals
    
    @staticmethod
    def combine_signals(*signal_series: pd.Series, 
                       threshold: int = 2) -> pd.Series:
        """Combine multiple signals with voting mechanism.
        
        Args:
            *signal_series: Multiple signal series to combine
            threshold: Minimum number of agreeing signals (default 2)
            
        Returns:
            Combined signal series
        """
        # Sum all signals
        combined = sum(signal_series)
        
        # Apply threshold
        final_signals = pd.Series(0, index=combined.index)
        final_signals[combined >= threshold] = 1  # Buy
        final_signals[combined <= -threshold] = -1  # Sell
        
        return final_signals