"""Data loading utilities for backtesting."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Load historical price data for backtesting."""
    
    @staticmethod
    def load_from_csv(filepath: str) -> pd.DataFrame:
        """
        Load OHLCV data from CSV file.
        
        Expected format:
        timestamp,open,high,low,close,volume
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            DataFrame with datetime index and OHLCV columns
        """
        df = pd.read_csv(filepath)
        
        # Parse timestamp
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        
        # Ensure required columns
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Sort by date
        df.sort_index(inplace=True)
        
        logger.info(f"Loaded {len(df)} bars from {filepath}")
        logger.info(f"Date range: {df.index[0]} to {df.index[-1]}")
        
        return df
    
    @staticmethod
    def load_from_binance(symbol: str, interval: str, 
                          start: datetime, end: datetime) -> pd.DataFrame:
        """
        Load historical data from Binance.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            interval: Timeframe (e.g., '1h', '1d')
            start: Start datetime
            end: End datetime
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            from binance.client import Client
            
            # Note: This requires API keys in environment
            client = Client()
            
            # Fetch klines
            klines = client.get_historical_klines(
                symbol,
                interval,
                start.strftime('%d %b %Y'),
                end.strftime('%d %b %Y')
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            # Parse and clean
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Convert to float
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            # Keep only OHLCV
            df = df[['open', 'high', 'low', 'close', 'volume']]
            
            logger.info(f"Loaded {len(df)} bars for {symbol} from Binance")
            return df
            
        except ImportError:
            logger.error("python-binance not installed. Run: pip install python-binance")
            raise
        except Exception as e:
            logger.error(f"Error loading data from Binance: {e}")
            raise
    
    @staticmethod
    def generate_sample_data(start: datetime, 
                           end: datetime,
                           initial_price: float = 50000.0,
                           volatility: float = 0.02,
                           freq: str = '1H') -> pd.DataFrame:
        """
        Generate synthetic OHLCV data for testing.
        
        Args:
            start: Start datetime
            end: End datetime
            initial_price: Starting price
            volatility: Price volatility (0.02 = 2%)
            freq: Frequency ('1H', '1D', etc.)
            
        Returns:
            DataFrame with synthetic OHLCV data
        """
        # Generate timestamps
        timestamps = pd.date_range(start=start, end=end, freq=freq)
        n = len(timestamps)
        
        # Generate random walk for close prices
        returns = np.random.normal(0, volatility, n)
        price_multipliers = np.exp(returns)
        close_prices = initial_price * np.cumprod(price_multipliers)
        
        # Generate OHLV
        data = []
        for i, (ts, close) in enumerate(zip(timestamps, close_prices)):
            # Generate high/low/open around close
            high = close * (1 + abs(np.random.normal(0, volatility/2)))
            low = close * (1 - abs(np.random.normal(0, volatility/2)))
            open_price = close * (1 + np.random.normal(0, volatility/3))
            
            # Ensure high >= close >= low and high >= open >= low
            high = max(high, close, open_price)
            low = min(low, close, open_price)
            
            volume = np.random.uniform(100, 1000)
            
            data.append({
                'timestamp': ts,
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        logger.info(f"Generated {len(df)} bars of synthetic data")
        logger.info(f"Price range: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
        
        return df
    
    @staticmethod
    def resample_data(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """
        Resample OHLCV data to different timeframe.
        
        Args:
            df: DataFrame with OHLCV data
            timeframe: Target timeframe ('5T', '1H', '1D', etc.)
            
        Returns:
            Resampled DataFrame
        """
        resampled = df.resample(timeframe).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        logger.info(f"Resampled to {timeframe}: {len(df)} -> {len(resampled)} bars")
        return resampled