"""Secure auto-trading bot with risk management."""
import robin_stocks.robinhood as r
from binance.client import Client
import time
import logging
from datetime import datetime
from typing import Optional, Dict
from config import config, logger
from risk_manager import risk_manager

class SecureTradingBot:
    """Secure trading bot with proper error handling and risk management."""
    
    def __init__(self):
        self.robinhood_logged_in = False
        self.binance_client: Optional[Client] = None
        self.last_buy_price: Optional[float] = None
        self.is_running = False
        
    def initialize(self) -> bool:
        """Initialize trading connections securely."""
        try:
            # Validate configuration
            if not config.validate():
                logger.error("Configuration validation failed")
                return False
            
            config.log_config()
            
            # Login to Robinhood
            logger.info("Logging into Robinhood...")
            login_response = r.login(
                config.ROBINHOOD_USERNAME,
                config.ROBINHOOD_PASSWORD
            )
            
            if login_response:
                self.robinhood_logged_in = True
                logger.info("✅ Successfully logged into Robinhood")
            else:
                logger.error("❌ Failed to login to Robinhood")
                return False
            
            # Initialize Binance client
            logger.info("Initializing Binance client...")
            self.binance_client = Client(
                config.BINANCE_API_KEY,
                config.BINANCE_API_SECRET
            )
            
            # Test Binance connection
            self.binance_client.ping()
            logger.info("✅ Successfully connected to Binance")
            
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            return False
    
    def get_binance_price(self, symbol: str) -> Optional[float]:
        """Get current price from Binance with error handling."""
        try:
            ticker = self.binance_client.get_symbol_ticker(
                symbol=symbol.replace('USD', 'USDT')
            )
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"Error fetching Binance price: {str(e)}")
            return None
    
    def get_last_buy_price(self, symbol: str) -> Optional[float]:
        """Get the last buy price from Robinhood order history."""
        try:
            orders = r.orders.get_all_crypto_orders()
            buys = [
                o for o in orders 
                if o['side'] == 'buy' 
                and o['state'] == 'filled' 
                and o['currency_pair_id'].startswith(symbol.lower())
            ]
            
            if not buys:
                return None
            
            last_buy = sorted(buys, key=lambda x: x['created_at'], reverse=True)[0]
            return float(last_buy['average_price'])
            
        except Exception as e:
            logger.error(f"Error fetching last buy price: {str(e)}")
            return None
    
    def execute_buy(self, symbol: str, quantity: float, price: float) -> bool:
        """Execute a buy order with safety checks."""
        try:
            # Check risk management
            can_trade, reason = risk_manager.can_trade(symbol, 'buy', quantity, price)
            
            if not can_trade:
                logger.warning(f"Trade blocked: {reason}")
                return False
            
            if config.DRY_RUN or config.PAPER_TRADING_MODE:
                logger.info(f"[DRY RUN] Would buy {quantity} {symbol} at ${price:.2f}")
                risk_manager.record_trade(symbol, 'buy', quantity, price)
                return True
            
            # Execute real trade
            logger.info(f"Executing BUY: {quantity} {symbol} at ${price:.2f}")
            result = r.orders.order_buy_crypto_by_quantity(symbol, quantity)
            
            if result:
                logger.info(f"✅ Buy order executed successfully")
                risk_manager.record_trade(symbol, 'buy', quantity, price)
                self.last_buy_price = price
                return True
            else:
                logger.error("❌ Buy order failed")
                return False
                
        except Exception as e:
            logger.error(f"Error executing buy order: {str(e)}")
            return False
    
    def execute_sell(self, symbol: str, quantity: float, price: float) -> bool:
        """Execute a sell order with safety checks."""
        try:
            # Check risk management
            can_trade, reason = risk_manager.can_trade(symbol, 'sell', quantity, price)
            
            if not can_trade:
                logger.warning(f"Trade blocked: {reason}")
                return False
            
            if config.DRY_RUN or config.PAPER_TRADING_MODE:
                logger.info(f"[DRY RUN] Would sell {quantity} {symbol} at ${price:.2f}")
                risk_manager.record_trade(symbol, 'sell', quantity, price)
                return True
            
            # Execute real trade
            logger.info(f"Executing SELL: {quantity} {symbol} at ${price:.2f}")
            result = r.orders.order_sell_crypto_by_quantity(symbol, quantity)
            
            if result:
                logger.info(f"✅ Sell order executed successfully")
                risk_manager.record_trade(symbol, 'sell', quantity, price)
                return True
            else:
                logger.error("❌ Sell order failed")
                return False
                
        except Exception as e:
            logger.error(f"Error executing sell order: {str(e)}")
            return False
    
    def trading_logic(self) -> None:
        """Main trading logic with improved strategy."""
        symbol = config.TRADING_SYMBOL
        quantity = config.TRADING_QUANTITY
        
        # Get current price
        current_price = self.get_binance_price(symbol)
        if current_price is None:
            logger.error("Failed to fetch current price")
            return
        
        # Get last buy price if not cached
        if self.last_buy_price is None:
            self.last_buy_price = self.get_last_buy_price(symbol)
        
        logger.info(f"Current {symbol} price: ${current_price:.2f}")
        logger.info(f"Last buy price: ${self.last_buy_price:.2f}" if self.last_buy_price else "No previous buy")
        
        # Get current position
        current_position = risk_manager.get_position(symbol)
        
        # Check for stop loss or take profit
        if current_position > 0 and self.last_buy_price:
            trigger = risk_manager.check_stop_loss_take_profit(
                symbol, current_price, self.last_buy_price
            )
            
            if trigger:
                logger.info(f"Trigger activated: {trigger}")
                self.execute_sell(symbol, quantity, current_price)
                return
        
        # Trading strategy
        if current_position == 0:  # No open position
            if self.last_buy_price is None or current_price < self.last_buy_price * 0.98:
                # Buy if price dropped 2% from last buy or no previous buy
                logger.info(f"Buy signal: Price favorable for entry")
                self.execute_buy(symbol, quantity, current_price)
        else:
            # Have open position, check take profit
            profit_pct = ((current_price - self.last_buy_price) / self.last_buy_price) * 100
            logger.info(f"Current P&L: {profit_pct:+.2f}%")
            
            if profit_pct >= config.TAKE_PROFIT_PERCENTAGE:
                logger.info(f"Take profit signal: {profit_pct:.2f}% gain")
                self.execute_sell(symbol, quantity, current_price)
    
    def run(self) -> None:
        """Main trading loop."""
        if not self.initialize():
            logger.error("Failed to initialize bot")
            return
        
        self.is_running = True
        logger.info(f"Starting trading loop (checking every {config.CHECK_INTERVAL_SECONDS}s)")
        logger.info("Press Ctrl+C to stop")
        
        try:
            iteration = 0
            while self.is_running:
                iteration += 1
                logger.info(f"\n{'='*60}")
                logger.info(f"Iteration #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*60}")
                
                # Execute trading logic
                self.trading_logic()
                
                # Log daily stats
                stats = risk_manager.get_daily_stats()
                logger.info(f"\nDaily Stats:")
                logger.info(f"  Trades: {stats['trades_today']}/{stats['max_trades']}")
                logger.info(f"  Remaining: {stats['trades_remaining']}")
                logger.info(f"  Open Positions: {stats['open_positions']}")
                
                # Wait for next iteration
                logger.info(f"\nWaiting {config.CHECK_INTERVAL_SECONDS} seconds...\n")
                time.sleep(config.CHECK_INTERVAL_SECONDS)
                
        except KeyboardInterrupt:
            logger.info("\n\nBot stopped by user")
            self.shutdown()
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            self.shutdown()
    
    def shutdown(self) -> None:
        """Cleanup and logout."""
        self.is_running = False
        
        if self.robinhood_logged_in:
            logger.info("Logging out from Robinhood...")
            r.logout()
        
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    bot = SecureTradingBot()
    bot.run()