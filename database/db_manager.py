"""Database manager for trading data persistence."""
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging

from database.models import Base, Trade, Position, DailyStats, Alert, PriceHistory, TradeType, TradeStatus

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, database_url: str = "sqlite:///trading_bot.db"):
        """Initialize database manager.
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.engine = create_engine(
            database_url,
            echo=False,  # Set to True for SQL logging
            pool_pre_ping=True
        )
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        
    def init_db(self):
        """Create all tables."""
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created")
    
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope for database operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            session.close()
    
    # Trade operations
    def record_trade(self, symbol: str, side: str, quantity: float, 
                    price: float, status: str = "executed",
                    strategy: str = None, notes: str = None) -> Trade:
        """Record a trade in the database.
        
        Args:
            symbol: Trading symbol
            side: 'buy' or 'sell'
            quantity: Amount traded
            price: Execution price
            status: Trade status
            strategy: Strategy name that triggered trade
            notes: Additional notes
        
        Returns:
            Trade object
        """
        with self.session_scope() as session:
            trade = Trade(
                symbol=symbol,
                side=TradeType.BUY if side.lower() == 'buy' else TradeType.SELL,
                quantity=quantity,
                price=price,
                total_value=quantity * price,
                status=TradeStatus[status.upper()],
                execution_time=datetime.utcnow(),
                strategy=strategy,
                notes=notes
            )
            session.add(trade)
            session.flush()
            logger.info(f"Recorded trade: {trade}")
            return trade
    
    def get_recent_trades(self, limit: int = 50, symbol: str = None) -> List[Trade]:
        """Get recent trades.
        
        Args:
            limit: Number of trades to return
            symbol: Filter by symbol (optional)
        
        Returns:
            List of Trade objects
        """
        with self.session_scope() as session:
            query = session.query(Trade).order_by(Trade.timestamp.desc())
            
            if symbol:
                query = query.filter(Trade.symbol == symbol)
            
            return query.limit(limit).all()
    
    def get_trades_by_date_range(self, start_date: datetime, end_date: datetime, 
                                 symbol: str = None) -> List[Trade]:
        """Get trades within date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            symbol: Filter by symbol (optional)
        
        Returns:
            List of Trade objects
        """
        with self.session_scope() as session:
            query = session.query(Trade).filter(
                Trade.timestamp >= start_date,
                Trade.timestamp <= end_date
            )
            
            if symbol:
                query = query.filter(Trade.symbol == symbol)
            
            return query.order_by(Trade.timestamp.desc()).all()
    
    # Position operations
    def update_position(self, symbol: str, quantity: float, 
                       entry_price: float, current_price: float = None) -> Position:
        """Update or create position.
        
        Args:
            symbol: Trading symbol
            quantity: Position quantity
            entry_price: Average entry price
            current_price: Current market price
        
        Returns:
            Position object
        """
        with self.session_scope() as session:
            position = session.query(Position).filter(
                Position.symbol == symbol,
                Position.is_open == True
            ).first()
            
            if position:
                # Update existing position
                position.quantity = quantity
                position.average_entry_price = entry_price
                position.current_price = current_price
                
                if current_price:
                    position.unrealized_pnl = (current_price - entry_price) * quantity
                    position.unrealized_pnl_percent = ((current_price - entry_price) / entry_price) * 100
                
                if quantity == 0:
                    position.is_open = False
                    position.closed_at = datetime.utcnow()
            else:
                # Create new position
                position = Position(
                    symbol=symbol,
                    quantity=quantity,
                    average_entry_price=entry_price,
                    current_price=current_price,
                    is_open=quantity > 0
                )
                session.add(position)
            
            session.flush()
            logger.info(f"Updated position: {position}")
            return position
    
    def get_open_positions(self) -> List[Position]:
        """Get all open positions.
        
        Returns:
            List of Position objects
        """
        with self.session_scope() as session:
            return session.query(Position).filter(Position.is_open == True).all()
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for specific symbol.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Position object or None
        """
        with self.session_scope() as session:
            return session.query(Position).filter(
                Position.symbol == symbol,
                Position.is_open == True
            ).first()
    
    # Daily stats operations
    def update_daily_stats(self, date: datetime, stats: Dict) -> DailyStats:
        """Update daily statistics.
        
        Args:
            date: Date for stats
            stats: Dictionary of statistics
        
        Returns:
            DailyStats object
        """
        with self.session_scope() as session:
            daily_stat = session.query(DailyStats).filter(
                func.date(DailyStats.date) == date.date()
            ).first()
            
            if not daily_stat:
                daily_stat = DailyStats(date=date)
                session.add(daily_stat)
            
            # Update stats
            for key, value in stats.items():
                if hasattr(daily_stat, key):
                    setattr(daily_stat, key, value)
            
            session.flush()
            logger.info(f"Updated daily stats for {date.date()}")
            return daily_stat
    
    def get_daily_stats(self, days: int = 30) -> List[DailyStats]:
        """Get daily stats for past N days.
        
        Args:
            days: Number of days to retrieve
        
        Returns:
            List of DailyStats objects
        """
        with self.session_scope() as session:
            start_date = datetime.utcnow() - timedelta(days=days)
            return session.query(DailyStats).filter(
                DailyStats.date >= start_date
            ).order_by(DailyStats.date.desc()).all()
    
    # Alert operations
    def create_alert(self, alert_type: str, severity: str, title: str, 
                    message: str, symbol: str = None, trade_id: int = None) -> Alert:
        """Create a new alert.
        
        Args:
            alert_type: Type of alert (trade, risk, error, info)
            severity: Severity level (low, medium, high, critical)
            title: Alert title
            message: Alert message
            symbol: Related symbol (optional)
            trade_id: Related trade ID (optional)
        
        Returns:
            Alert object
        """
        with self.session_scope() as session:
            alert = Alert(
                alert_type=alert_type,
                severity=severity,
                title=title,
                message=message,
                symbol=symbol,
                trade_id=trade_id
            )
            session.add(alert)
            session.flush()
            logger.info(f"Created alert: {alert}")
            return alert
    
    def get_unacknowledged_alerts(self, severity: str = None) -> List[Alert]:
        """Get unacknowledged alerts.
        
        Args:
            severity: Filter by severity (optional)
        
        Returns:
            List of Alert objects
        """
        with self.session_scope() as session:
            query = session.query(Alert).filter(Alert.acknowledged == False)
            
            if severity:
                query = query.filter(Alert.severity == severity)
            
            return query.order_by(Alert.timestamp.desc()).all()
    
    def acknowledge_alert(self, alert_id: int):
        """Mark alert as acknowledged.
        
        Args:
            alert_id: Alert ID
        """
        with self.session_scope() as session:
            alert = session.query(Alert).filter(Alert.id == alert_id).first()
            if alert:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.utcnow()
                logger.info(f"Acknowledged alert {alert_id}")
    
    # Price history operations
    def record_price(self, symbol: str, timestamp: datetime, 
                    open_price: float, high: float, low: float, 
                    close: float, volume: float = 0.0, 
                    source: str = "binance") -> PriceHistory:
        """Record historical price data.
        
        Args:
            symbol: Trading symbol
            timestamp: Price timestamp
            open_price: Opening price
            high: High price
            low: Low price
            close: Closing price
            volume: Trading volume
            source: Data source
        
        Returns:
            PriceHistory object
        """
        with self.session_scope() as session:
            price = PriceHistory(
                symbol=symbol,
                timestamp=timestamp,
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=volume,
                source=source
            )
            session.add(price)
            return price
    
    def get_price_history(self, symbol: str, start_date: datetime, 
                         end_date: datetime = None) -> List[PriceHistory]:
        """Get price history for symbol.
        
        Args:
            symbol: Trading symbol
            start_date: Start date
            end_date: End date (defaults to now)
        
        Returns:
            List of PriceHistory objects
        """
        if not end_date:
            end_date = datetime.utcnow()
        
        with self.session_scope() as session:
            return session.query(PriceHistory).filter(
                PriceHistory.symbol == symbol,
                PriceHistory.timestamp >= start_date,
                PriceHistory.timestamp <= end_date
            ).order_by(PriceHistory.timestamp.asc()).all()


# Global instance
db = DatabaseManager()