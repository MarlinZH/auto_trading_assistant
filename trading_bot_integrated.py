"""Enhanced trading bot with database and alert integration."""
import robin_stocks.robinhood as r
from binance.client import Client
import time
import logging
from datetime import datetime
from typing import Optional

from config_updated import config, logger
from risk_manager import risk_manager
from database.db_manager import db
from alerts.notifier import notifier


class EnhancedTradingBot:
    """Trading bot with full infrastructure integration."""
    
    def __init__(self):
        self.robinhood_logged_in = False
        self.binance_client: Optional[Client] = None
        self.last_buy_price: Optional[float] = None
        self.is_running = False
        
    def initialize(self) -> bool:
        """Initialize trading connections and database."""
        try:
            # Validate configuration
            if not config.validate():
                logger.error("Configuration validation failed")
                return False
            
            config.log_config()
            
            # Initialize database
            logger.info("Initializing database...")
            db.init_db()
            logger.info("✅ Database initialized")
            
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
                notifier.send_error_alert("Failed to login to Robinhood")
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
            notifier.send_error_alert(str(e), "Bot initialization")
            return False
    
    def get_binance_price(self, symbol: str) -> Optional[float]:
        """Get current price from Binance."""
        try:
            ticker = self.binance_client.get_symbol_ticker(
                symbol=symbol.replace('USD', 'USDT')
            )
            price = float(ticker['price'])
            
            # Record price history
            db.record_price(
                symbol=symbol,
                timestamp=datetime.utcnow(),
                open_price=price,
                high=price,
                low=price,
                close=price,
                source='binance'
            )
            
            return price
        except Exception as e:
            logger.error(f"Error fetching Binance price: {str(e)}")
            return None
    
    def execute_buy(self, symbol: str, quantity: float, price: float) -> bool:
        """Execute buy order with database and alert integration."""
        try:
            # Check risk management
            can_trade, reason = risk_manager.can_trade(symbol, 'buy', quantity, price)
            
            if not can_trade:
                logger.warning(f"Trade blocked: {reason}")
                return False
            
            if config.DRY_RUN or config.PAPER_TRADING_MODE:
                logger.info(f"[DRY RUN] Would buy {quantity} {symbol} at ${price:.2f}")
                success = True
            else:
                # Execute real trade
                logger.info(f"Executing BUY: {quantity} {symbol} at ${price:.2f}")
                result = r.orders.order_buy_crypto_by_quantity(symbol, quantity)
                success = bool(result)
            
            if success:
                # Record trade in database
                trade = db.record_trade(
                    symbol=symbol,
                    side='buy',
                    quantity=quantity,
                    price=price,
                    status='executed',
                    strategy='momentum'
                )
                
                # Update position
                db.update_position(
                    symbol=symbol,
                    quantity=quantity,
                    entry_price=price,
                    current_price=price
                )
                
                # Update risk manager
                risk_manager.record_trade(symbol, 'buy', quantity, price)
                self.last_buy_price = price
                
                # Send alert
                if config.ALERT_ON_TRADE:
                    notifier.send_trade_alert(symbol, 'buy', quantity, price)
                
                logger.info(f"✅ Buy order executed successfully (Trade ID: {trade.id})")
                return True
            else:
                logger.error("❌ Buy order failed")
                return False
                
        except Exception as e:
            logger.error(f"Error executing buy order: {str(e)}")
            notifier.send_error_alert(str(e), f"Buy order for {symbol}")
            return False
    
    def execute_sell(self, symbol: str, quantity: float, price: float, 
                    entry_price: float = None, trigger: str = None) -> bool:
        """Execute sell order with P&L tracking."""
        try:
            # Check risk management
            can_trade, reason = risk_manager.can_trade(symbol, 'sell', quantity, price)
            
            if not can_trade:
                logger.warning(f"Trade blocked: {reason}")
                return False
            
            if config.DRY_RUN or config.PAPER_TRADING_MODE:
                logger.info(f"[DRY RUN] Would sell {quantity} {symbol} at ${price:.2f}")
                success = True
            else:
                # Execute real trade
                logger.info(f"Executing SELL: {quantity} {symbol} at ${price:.2f}")
                result = r.orders.order_sell_crypto_by_quantity(symbol, quantity)
                success = bool(result)
            
            if success:
                # Calculate P&L
                pnl = 0
                if entry_price:
                    pnl = (price - entry_price) * quantity
                
                # Record trade in database
                trade = db.record_trade(
                    symbol=symbol,
                    side='sell',
                    quantity=quantity,
                    price=price,
                    status='executed',
                    strategy='momentum',
                    notes=f"Trigger: {trigger}" if trigger else None
                )
                
                # Update trade with P&L
                with db.session_scope() as session:
                    trade.realized_pnl = pnl
                
                # Update position
                db.update_position(
                    symbol=symbol,
                    quantity=0,
                    entry_price=entry_price or price,
                    current_price=price
                )
                
                # Update risk manager
                risk_manager.record_trade(symbol, 'sell', quantity, price)
                
                # Send appropriate alert
                if trigger == 'stop_loss' and config.ALERT_ON_STOP_LOSS:
                    notifier.send_stop_loss_alert(symbol, entry_price, price, pnl)
                elif trigger == 'take_profit' and config.ALERT_ON_TAKE_PROFIT:
                    notifier.send_take_profit_alert(symbol, entry_price, price, pnl)
                elif config.ALERT_ON_TRADE:
                    notifier.send_trade_alert(symbol, 'sell', quantity, price)
                
                logger.info(f"✅ Sell order executed (Trade ID: {trade.id}, P&L: ${pnl:.2f})")
                return True
            else:
                logger.error("❌ Sell order failed")
                return False
                
        except Exception as e:
            logger.error(f"Error executing sell order: {str(e)}")
            notifier.send_error_alert(str(e), f"Sell order for {symbol}")
            return False
    
    def trading_logic(self) -> None:
        """Main trading logic."""
        symbol = config.TRADING_SYMBOL
        quantity = config.TRADING_QUANTITY
        
        # Get current price
        current_price = self.get_binance_price(symbol)
        if current_price is None:
            logger.error("Failed to fetch current price")
            return
        
        # Get or create position
        position = db.get_position(symbol)
        current_position = position.quantity if position else 0
        entry_price = position.average_entry_price if position else self.last_buy_price
        
        logger.info(f"Current {symbol} price: ${current_price:.2f}")
        if entry_price:
            logger.info(f"Entry price: ${entry_price:.2f}")
        
        # Check for stop loss or take profit
        if current_position > 0 and entry_price:
            trigger = risk_manager.check_stop_loss_take_profit(
                symbol, current_price, entry_price
            )
            
            if trigger:
                logger.info(f"Trigger activated: {trigger}")
                self.execute_sell(symbol, quantity, current_price, entry_price, trigger)
                return
            
            # Update position with current price
            db.update_position(symbol, current_position, entry_price, current_price)
        
        # Trading strategy
        if current_position == 0:
            if not entry_price or current_price < entry_price * 0.98:
                logger.info(f"Buy signal: Price favorable for entry")
                self.execute_buy(symbol, quantity, current_price)
        else:
            profit_pct = ((current_price - entry_price) / entry_price) * 100
            logger.info(f"Current P&L: {profit_pct:+.2f}%")
            
            if profit_pct >= config.TAKE_PROFIT_PERCENTAGE:
                logger.info(f"Take profit signal: {profit_pct:.2f}% gain")
                self.execute_sell(symbol, quantity, current_price, entry_price, 'take_profit')
    
    def update_daily_stats(self):
        """Update daily statistics."""
        try:
            stats = risk_manager.get_daily_stats()
            
            # Add more stats from database
            with db.session_scope() as session:
                from datetime import timedelta
                today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                
                winning = session.query(db.Trade).filter(
                    db.Trade.timestamp >= today,
                    db.Trade.realized_pnl > 0
                ).count()
                
                losing = session.query(db.Trade).filter(
                    db.Trade.timestamp >= today,
                    db.Trade.realized_pnl < 0
                ).count()
                
                total_pnl = session.query(db.func.sum(db.Trade.realized_pnl)).filter(
                    db.Trade.timestamp >= today
                ).scalar() or 0
                
                stats.update({
                    'winning_trades': winning,
                    'losing_trades': losing,
                    'realized_pnl': total_pnl,
                    'win_rate': (winning / (winning + losing) * 100) if (winning + losing) > 0 else 0
                })
            
            db.update_daily_stats(datetime.utcnow(), stats)
        
        except Exception as e:
            logger.error(f"Error updating daily stats: {str(e)}")
    
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
                
                # Update daily stats
                if iteration % 10 == 0:  # Every 10 iterations
                    self.update_daily_stats()
                
                # Log stats
                stats = risk_manager.get_daily_stats()
                logger.info(f"\nDaily Stats:")
                logger.info(f"  Trades: {stats['trades_today']}/{stats['max_trades']}")
                logger.info(f"  Remaining: {stats['trades_remaining']}")
                logger.info(f"  Open Positions: {len(stats['open_positions'])}")
                
                # Wait for next iteration
                logger.info(f"\nWaiting {config.CHECK_INTERVAL_SECONDS} seconds...\n")
                time.sleep(config.CHECK_INTERVAL_SECONDS)
                
        except KeyboardInterrupt:
            logger.info("\n\nBot stopped by user")
            self.shutdown()
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            notifier.send_error_alert(str(e), "Main trading loop")
            self.shutdown()
    
    def shutdown(self) -> None:
        """Cleanup and logout."""
        self.is_running = False
        
        # Update final stats
        self.update_daily_stats()
        
        if self.robinhood_logged_in:
            logger.info("Logging out from Robinhood...")
            r.logout()
        
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    bot = EnhancedTradingBot()
    bot.run()