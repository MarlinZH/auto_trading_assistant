"""Secure configuration management for trading assistant."""
import os
from typing import Optional
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Config:
    """Centralized configuration with validation."""
    
    # Robinhood
    ROBINHOOD_USERNAME: Optional[str] = os.getenv('ROBINHOOD_USERNAME')
    ROBINHOOD_PASSWORD: Optional[str] = os.getenv('ROBINHOOD_PASSWORD')
    
    # Binance
    BINANCE_API_KEY: Optional[str] = os.getenv('BINANCE_API_KEY')
    BINANCE_API_SECRET: Optional[str] = os.getenv('BINANCE_API_SECRET')
    
    # Notion
    NOTION_API_KEY: Optional[str] = os.getenv('NOTION_API_KEY')
    NOTION_DATABASE_ID: Optional[str] = os.getenv('NOTION_DATABASE_ID')
    
    # Trading settings
    TRADING_SYMBOL: str = os.getenv('TRADING_SYMBOL', 'BTCUSD')
    TRADING_QUANTITY: float = float(os.getenv('TRADING_QUANTITY', '0.001'))
    CHECK_INTERVAL_SECONDS: int = int(os.getenv('CHECK_INTERVAL_SECONDS', '60'))
    
    # Risk management
    MAX_POSITION_SIZE: float = float(os.getenv('MAX_POSITION_SIZE', '1000'))
    STOP_LOSS_PERCENTAGE: float = float(os.getenv('STOP_LOSS_PERCENTAGE', '5.0'))
    TAKE_PROFIT_PERCENTAGE: float = float(os.getenv('TAKE_PROFIT_PERCENTAGE', '10.0'))
    MAX_DAILY_TRADES: int = int(os.getenv('MAX_DAILY_TRADES', '10'))
    
    # Safety mode
    PAPER_TRADING_MODE: bool = os.getenv('PAPER_TRADING_MODE', 'true').lower() == 'true'
    DRY_RUN: bool = os.getenv('DRY_RUN', 'true').lower() == 'true'
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required credentials are present."""
        missing = []
        
        if not cls.ROBINHOOD_USERNAME:
            missing.append('ROBINHOOD_USERNAME')
        if not cls.ROBINHOOD_PASSWORD:
            missing.append('ROBINHOOD_PASSWORD')
        if not cls.BINANCE_API_KEY:
            missing.append('BINANCE_API_KEY')
        if not cls.BINANCE_API_SECRET:
            missing.append('BINANCE_API_SECRET')
        
        if missing:
            logger.error(f"Missing required environment variables: {', '.join(missing)}")
            logger.error("Please create a .env file based on .env.example")
            return False
        
        # Validate credentials are not placeholder values
        if 'your_' in cls.ROBINHOOD_USERNAME.lower():
            logger.error("Please replace placeholder values in .env file")
            return False
        
        return True
    
    @classmethod
    def log_config(cls) -> None:
        """Log configuration (without sensitive data)."""
        logger.info("=" * 50)
        logger.info("Trading Bot Configuration")
        logger.info("=" * 50)
        logger.info(f"Symbol: {cls.TRADING_SYMBOL}")
        logger.info(f"Quantity: {cls.TRADING_QUANTITY}")
        logger.info(f"Check Interval: {cls.CHECK_INTERVAL_SECONDS}s")
        logger.info(f"Stop Loss: {cls.STOP_LOSS_PERCENTAGE}%")
        logger.info(f"Take Profit: {cls.TAKE_PROFIT_PERCENTAGE}%")
        logger.info(f"Max Daily Trades: {cls.MAX_DAILY_TRADES}")
        logger.info(f"Paper Trading Mode: {cls.PAPER_TRADING_MODE}")
        logger.info(f"Dry Run: {cls.DRY_RUN}")
        logger.info("=" * 50)
        
        if cls.PAPER_TRADING_MODE or cls.DRY_RUN:
            logger.warning("⚠️  SAFETY MODE ENABLED - No real trades will be executed")
            logger.warning("⚠️  Set PAPER_TRADING_MODE=false and DRY_RUN=false to enable live trading")

config = Config()