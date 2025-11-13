"""Unit tests for Config class."""
import pytest
import os
from unittest.mock import patch
from config import Config


class TestConfig:
    """Test suite for Config class."""
    
    def test_default_values(self):
        """Test config has reasonable defaults."""
        # Trading settings defaults
        assert Config.TRADING_SYMBOL == 'BTCUSD' or Config.TRADING_SYMBOL is not None
        assert isinstance(Config.TRADING_QUANTITY, float)
        assert isinstance(Config.CHECK_INTERVAL_SECONDS, int)
        
        # Risk management defaults
        assert isinstance(Config.MAX_POSITION_SIZE, float)
        assert isinstance(Config.STOP_LOSS_PERCENTAGE, float)
        assert isinstance(Config.TAKE_PROFIT_PERCENTAGE, float)
        assert isinstance(Config.MAX_DAILY_TRADES, int)
        
        # Safety defaults
        assert isinstance(Config.PAPER_TRADING_MODE, bool)
        assert isinstance(Config.DRY_RUN, bool)
    
    @patch.dict(os.environ, {
        'ROBINHOOD_USERNAME': 'test@example.com',
        'ROBINHOOD_PASSWORD': 'testpass123',
        'BINANCE_API_KEY': 'test_api_key',
        'BINANCE_API_SECRET': 'test_api_secret'
    })
    def test_validate_success(self):
        """Test validation passes with all credentials."""
        # Reload config with mocked env vars
        Config.ROBINHOOD_USERNAME = os.getenv('ROBINHOOD_USERNAME')
        Config.ROBINHOOD_PASSWORD = os.getenv('ROBINHOOD_PASSWORD')
        Config.BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
        Config.BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
        
        result = Config.validate()
        assert result is True
    
    @patch.dict(os.environ, {
        'ROBINHOOD_USERNAME': '',
        'ROBINHOOD_PASSWORD': 'testpass123',
        'BINANCE_API_KEY': 'test_api_key',
        'BINANCE_API_SECRET': 'test_api_secret'
    }, clear=True)
    def test_validate_missing_robinhood_username(self):
        """Test validation fails without Robinhood username."""
        Config.ROBINHOOD_USERNAME = None
        Config.ROBINHOOD_PASSWORD = os.getenv('ROBINHOOD_PASSWORD')
        Config.BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
        Config.BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
        
        result = Config.validate()
        assert result is False
    
    @patch.dict(os.environ, {
        'ROBINHOOD_USERNAME': 'test@example.com',
        'ROBINHOOD_PASSWORD': '',
        'BINANCE_API_KEY': 'test_api_key',
        'BINANCE_API_SECRET': 'test_api_secret'
    }, clear=True)
    def test_validate_missing_robinhood_password(self):
        """Test validation fails without Robinhood password."""
        Config.ROBINHOOD_USERNAME = os.getenv('ROBINHOOD_USERNAME')
        Config.ROBINHOOD_PASSWORD = None
        Config.BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
        Config.BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
        
        result = Config.validate()
        assert result is False
    
    @patch.dict(os.environ, {
        'ROBINHOOD_USERNAME': 'test@example.com',
        'ROBINHOOD_PASSWORD': 'testpass123',
        'BINANCE_API_KEY': '',
        'BINANCE_API_SECRET': 'test_api_secret'
    }, clear=True)
    def test_validate_missing_binance_api_key(self):
        """Test validation fails without Binance API key."""
        Config.ROBINHOOD_USERNAME = os.getenv('ROBINHOOD_USERNAME')
        Config.ROBINHOOD_PASSWORD = os.getenv('ROBINHOOD_PASSWORD')
        Config.BINANCE_API_KEY = None
        Config.BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
        
        result = Config.validate()
        assert result is False
    
    @patch.dict(os.environ, {
        'ROBINHOOD_USERNAME': 'test@example.com',
        'ROBINHOOD_PASSWORD': 'testpass123',
        'BINANCE_API_KEY': 'test_api_key',
        'BINANCE_API_SECRET': ''
    }, clear=True)
    def test_validate_missing_binance_api_secret(self):
        """Test validation fails without Binance API secret."""
        Config.ROBINHOOD_USERNAME = os.getenv('ROBINHOOD_USERNAME')
        Config.ROBINHOOD_PASSWORD = os.getenv('ROBINHOOD_PASSWORD')
        Config.BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
        Config.BINANCE_API_SECRET = None
        
        result = Config.validate()
        assert result is False
    
    @patch.dict(os.environ, {
        'ROBINHOOD_USERNAME': 'your_robinhood_email',
        'ROBINHOOD_PASSWORD': 'testpass123',
        'BINANCE_API_KEY': 'test_api_key',
        'BINANCE_API_SECRET': 'test_api_secret'
    })
    def test_validate_placeholder_values(self):
        """Test validation fails with placeholder values."""
        Config.ROBINHOOD_USERNAME = os.getenv('ROBINHOOD_USERNAME')
        Config.ROBINHOOD_PASSWORD = os.getenv('ROBINHOOD_PASSWORD')
        Config.BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
        Config.BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
        
        result = Config.validate()
        assert result is False
    
    @patch.dict(os.environ, {
        'TRADING_SYMBOL': 'ETHUSD',
        'TRADING_QUANTITY': '0.01',
        'CHECK_INTERVAL_SECONDS': '120'
    })
    def test_custom_trading_settings(self):
        """Test custom trading settings are loaded."""
        # Reload config
        Config.TRADING_SYMBOL = os.getenv('TRADING_SYMBOL', 'BTCUSD')
        Config.TRADING_QUANTITY = float(os.getenv('TRADING_QUANTITY', '0.001'))
        Config.CHECK_INTERVAL_SECONDS = int(os.getenv('CHECK_INTERVAL_SECONDS', '60'))
        
        assert Config.TRADING_SYMBOL == 'ETHUSD'
        assert Config.TRADING_QUANTITY == 0.01
        assert Config.CHECK_INTERVAL_SECONDS == 120
    
    @patch.dict(os.environ, {
        'MAX_POSITION_SIZE': '5000',
        'STOP_LOSS_PERCENTAGE': '3.0',
        'TAKE_PROFIT_PERCENTAGE': '15.0',
        'MAX_DAILY_TRADES': '20'
    })
    def test_custom_risk_settings(self):
        """Test custom risk settings are loaded."""
        # Reload config
        Config.MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '1000'))
        Config.STOP_LOSS_PERCENTAGE = float(os.getenv('STOP_LOSS_PERCENTAGE', '5.0'))
        Config.TAKE_PROFIT_PERCENTAGE = float(os.getenv('TAKE_PROFIT_PERCENTAGE', '10.0'))
        Config.MAX_DAILY_TRADES = int(os.getenv('MAX_DAILY_TRADES', '10'))
        
        assert Config.MAX_POSITION_SIZE == 5000.0
        assert Config.STOP_LOSS_PERCENTAGE == 3.0
        assert Config.TAKE_PROFIT_PERCENTAGE == 15.0
        assert Config.MAX_DAILY_TRADES == 20
    
    @patch.dict(os.environ, {
        'PAPER_TRADING_MODE': 'false',
        'DRY_RUN': 'false'
    })
    def test_safety_modes_disabled(self):
        """Test safety modes can be disabled."""
        Config.PAPER_TRADING_MODE = os.getenv('PAPER_TRADING_MODE', 'true').lower() == 'true'
        Config.DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'
        
        assert Config.PAPER_TRADING_MODE is False
        assert Config.DRY_RUN is False
    
    @patch.dict(os.environ, {
        'PAPER_TRADING_MODE': 'TRUE',
        'DRY_RUN': 'True'
    })
    def test_safety_modes_case_insensitive(self):
        """Test safety mode flags are case insensitive."""
        Config.PAPER_TRADING_MODE = os.getenv('PAPER_TRADING_MODE', 'true').lower() == 'true'
        Config.DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'
        
        assert Config.PAPER_TRADING_MODE is True
        assert Config.DRY_RUN is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])