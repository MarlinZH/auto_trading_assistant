"""Database models for trading history and analytics."""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class TradeType(enum.Enum):
    """Trade side enumeration."""
    BUY = "buy"
    SELL = "sell"


class TradeStatus(enum.Enum):
    """Trade status enumeration."""
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Trade(Base):
    """Trade execution record."""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(Enum(TradeType), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)  # quantity * price
    status = Column(Enum(TradeStatus), default=TradeStatus.PENDING, nullable=False)
    
    # Execution details
    execution_time = Column(DateTime)
    order_id = Column(String(100))
    
    # P&L tracking
    realized_pnl = Column(Float, default=0.0)
    
    # Metadata
    strategy = Column(String(50))  # Strategy that triggered trade
    notes = Column(Text)
    
    def __repr__(self):
        return f"<Trade(id={self.id}, {self.side.value} {self.quantity} {self.symbol} @ ${self.price:.2f})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'symbol': self.symbol,
            'side': self.side.value,
            'quantity': self.quantity,
            'price': self.price,
            'total_value': self.total_value,
            'status': self.status.value,
            'execution_time': self.execution_time.isoformat() if self.execution_time else None,
            'order_id': self.order_id,
            'realized_pnl': self.realized_pnl,
            'strategy': self.strategy,
            'notes': self.notes
        }


class Position(Base):
    """Current position tracking."""
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, unique=True, index=True)
    quantity = Column(Float, nullable=False, default=0.0)
    average_entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    
    # P&L
    unrealized_pnl = Column(Float, default=0.0)
    unrealized_pnl_percent = Column(Float, default=0.0)
    
    # Tracking
    opened_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_open = Column(Boolean, default=True, nullable=False, index=True)
    closed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Position(symbol={self.symbol}, qty={self.quantity}, entry=${self.average_entry_price:.2f})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'quantity': self.quantity,
            'average_entry_price': self.average_entry_price,
            'current_price': self.current_price,
            'unrealized_pnl': self.unrealized_pnl,
            'unrealized_pnl_percent': self.unrealized_pnl_percent,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'is_open': self.is_open,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None
        }


class DailyStats(Base):
    """Daily trading statistics."""
    __tablename__ = 'daily_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, unique=True, index=True)
    
    # Trading activity
    trades_count = Column(Integer, default=0)
    buy_count = Column(Integer, default=0)
    sell_count = Column(Integer, default=0)
    
    # Volume
    total_volume = Column(Float, default=0.0)
    
    # P&L
    realized_pnl = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    
    # Win rate
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)  # Percentage
    
    # Risk metrics
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float)
    
    def __repr__(self):
        return f"<DailyStats(date={self.date.date()}, trades={self.trades_count}, pnl=${self.total_pnl:.2f})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'date': self.date.date().isoformat() if self.date else None,
            'trades_count': self.trades_count,
            'buy_count': self.buy_count,
            'sell_count': self.sell_count,
            'total_volume': self.total_volume,
            'realized_pnl': self.realized_pnl,
            'unrealized_pnl': self.unrealized_pnl,
            'total_pnl': self.total_pnl,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio
        }


class Alert(Base):
    """Alert/notification tracking."""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False, index=True)  # trade, risk, error, info
    severity = Column(String(20), nullable=False, index=True)  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Related data
    symbol = Column(String(20))
    trade_id = Column(Integer)
    
    # Notification status
    sent = Column(Boolean, default=False, nullable=False)
    sent_at = Column(DateTime)
    delivery_method = Column(String(50))  # email, webhook, sms
    
    # User acknowledgment
    acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Alert(type={self.alert_type}, severity={self.severity}, title={self.title})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'title': self.title,
            'message': self.message,
            'symbol': self.symbol,
            'trade_id': self.trade_id,
            'sent': self.sent,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivery_method': self.delivery_method,
            'acknowledged': self.acknowledged,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None
        }


class PriceHistory(Base):
    """Historical price data for analysis."""
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # OHLCV data
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, default=0.0)
    
    # Source
    source = Column(String(50))  # binance, robinhood, etc.
    
    def __repr__(self):
        return f"<PriceHistory(symbol={self.symbol}, time={self.timestamp}, close=${self.close:.2f})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'symbol': self.symbol,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'source': self.source
        }