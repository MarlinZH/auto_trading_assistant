"""Risk management module for trading operations."""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from config import config

logger = logging.getLogger(__name__)

@dataclass
class Trade:
    """Trade record."""
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    price: float
    timestamp: datetime
    
class RiskManager:
    """Manages trading risk and position limits."""
    
    def __init__(self):
        self.daily_trades: List[Trade] = []
        self.positions: Dict[str, float] = {}  # symbol -> quantity
        self.daily_pnl: float = 0.0
        self.last_reset: datetime = datetime.now()
        
    def reset_daily_counters(self) -> None:
        """Reset daily counters if new day."""
        if datetime.now().date() > self.last_reset.date():
            logger.info("New trading day - resetting counters")
            self.daily_trades = []
            self.daily_pnl = 0.0
            self.last_reset = datetime.now()
    
    def can_trade(self, symbol: str, side: str, quantity: float, price: float) -> tuple[bool, str]:
        """Check if trade is allowed based on risk parameters."""
        self.reset_daily_counters()
        
        # Check if in paper trading mode
        if config.PAPER_TRADING_MODE or config.DRY_RUN:
            logger.info(f"[PAPER TRADE] Would {side} {quantity} {symbol} at ${price}")
            return True, "Paper trading mode"
        
        # Check daily trade limit
        if len(self.daily_trades) >= config.MAX_DAILY_TRADES:
            msg = f"Daily trade limit reached ({config.MAX_DAILY_TRADES})"
            logger.warning(msg)
            return False, msg
        
        # Check position size
        trade_value = quantity * price
        if trade_value > config.MAX_POSITION_SIZE:
            msg = f"Trade value ${trade_value:.2f} exceeds max position size ${config.MAX_POSITION_SIZE}"
            logger.warning(msg)
            return False, msg
        
        # Check if we have an open position
        current_position = self.positions.get(symbol, 0)
        
        if side == 'buy' and current_position > 0:
            msg = f"Already have open position for {symbol}: {current_position}"
            logger.warning(msg)
            return False, msg
        
        if side == 'sell' and current_position <= 0:
            msg = f"No open position to sell for {symbol}"
            logger.warning(msg)
            return False, msg
        
        return True, "Trade allowed"
    
    def record_trade(self, symbol: str, side: str, quantity: float, price: float) -> None:
        """Record a trade."""
        trade = Trade(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            timestamp=datetime.now()
        )
        
        self.daily_trades.append(trade)
        
        # Update position
        if side == 'buy':
            self.positions[symbol] = self.positions.get(symbol, 0) + quantity
            logger.info(f"Opened position: {quantity} {symbol} at ${price}")
        elif side == 'sell':
            self.positions[symbol] = self.positions.get(symbol, 0) - quantity
            logger.info(f"Closed position: {quantity} {symbol} at ${price}")
    
    def check_stop_loss_take_profit(self, symbol: str, current_price: float, 
                                     entry_price: float) -> Optional[str]:
        """Check if stop loss or take profit should trigger."""
        if symbol not in self.positions or self.positions[symbol] == 0:
            return None
        
        price_change_pct = ((current_price - entry_price) / entry_price) * 100
        
        if price_change_pct <= -config.STOP_LOSS_PERCENTAGE:
            logger.warning(f"⛔ Stop loss triggered for {symbol}: {price_change_pct:.2f}%")
            return 'stop_loss'
        
        if price_change_pct >= config.TAKE_PROFIT_PERCENTAGE:
            logger.info(f"✅ Take profit triggered for {symbol}: {price_change_pct:.2f}%")
            return 'take_profit'
        
        return None
    
    def get_position(self, symbol: str) -> float:
        """Get current position for symbol."""
        return self.positions.get(symbol, 0)
    
    def get_daily_stats(self) -> Dict:
        """Get daily trading statistics."""
        return {
            'trades_today': len(self.daily_trades),
            'max_trades': config.MAX_DAILY_TRADES,
            'trades_remaining': max(0, config.MAX_DAILY_TRADES - len(self.daily_trades)),
            'daily_pnl': self.daily_pnl,
            'open_positions': {k: v for k, v in self.positions.items() if v != 0}
        }

risk_manager = RiskManager()