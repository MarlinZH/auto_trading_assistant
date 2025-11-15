"""Alert notification system."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import logging
from typing import Optional
from datetime import datetime

from database.db_manager import db
from config import Config

logger = logging.getLogger(__name__)


class AlertNotifier:
    """Manages alert notifications via multiple channels."""
    
    def __init__(self):
        self.email_enabled = bool(Config.SMTP_SERVER and Config.EMAIL_FROM)
        self.webhook_enabled = bool(Config.WEBHOOK_URL)
        
        if not self.email_enabled and not self.webhook_enabled:
            logger.warning("No notification channels configured")
    
    def send_alert(self, alert_type: str, severity: str, title: str, 
                   message: str, symbol: str = None, trade_id: int = None):
        """Send alert via all configured channels.
        
        Args:
            alert_type: Type of alert (trade, risk, error, info)
            severity: Severity level (low, medium, high, critical)
            title: Alert title
            message: Alert message
            symbol: Related symbol (optional)
            trade_id: Related trade ID (optional)
        """
        # Record in database
        alert = db.create_alert(
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            symbol=symbol,
            trade_id=trade_id
        )
        
        # Send notifications
        if self.email_enabled:
            self._send_email(alert)
        
        if self.webhook_enabled:
            self._send_webhook(alert)
    
    def _send_email(self, alert) -> bool:
        """Send email notification.
        
        Args:
            alert: Alert object
        
        Returns:
            True if successful
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = Config.EMAIL_FROM
            msg['To'] = Config.EMAIL_TO
            msg['Subject'] = f"[{alert.severity.upper()}] {alert.title}"
            
            # Email body
            body = f"""
            Trading Alert
            
            Type: {alert.alert_type}
            Severity: {alert.severity}
            Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
            Symbol: {alert.symbol or 'N/A'}
            
            {alert.message}
            
            ---
            Auto Trading Assistant
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                if Config.SMTP_USE_TLS:
                    server.starttls()
                
                if Config.SMTP_USERNAME and Config.SMTP_PASSWORD:
                    server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
                
                server.send_message(msg)
            
            logger.info(f"Email sent for alert {alert.id}")
            
            # Update alert
            with db.session_scope() as session:
                alert = session.query(db.Alert).filter(db.Alert.id == alert.id).first()
                alert.sent = True
                alert.sent_at = datetime.utcnow()
                alert.delivery_method = 'email'
            
            return True
        
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def _send_webhook(self, alert) -> bool:
        """Send webhook notification.
        
        Args:
            alert: Alert object
        
        Returns:
            True if successful
        """
        try:
            payload = {
                'type': alert.alert_type,
                'severity': alert.severity,
                'title': alert.title,
                'message': alert.message,
                'symbol': alert.symbol,
                'trade_id': alert.trade_id,
                'timestamp': alert.timestamp.isoformat()
            }
            
            # Send to webhook
            response = requests.post(
                Config.WEBHOOK_URL,
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            
            logger.info(f"Webhook sent for alert {alert.id}")
            
            # Update alert
            with db.session_scope() as session:
                alert = session.query(db.Alert).filter(db.Alert.id == alert.id).first()
                alert.sent = True
                alert.sent_at = datetime.utcnow()
                alert.delivery_method = 'webhook'
            
            return True
        
        except Exception as e:
            logger.error(f"Error sending webhook: {str(e)}")
            return False
    
    def send_trade_alert(self, symbol: str, side: str, quantity: float, price: float):
        """Send alert for trade execution.
        
        Args:
            symbol: Trading symbol
            side: buy or sell
            quantity: Amount traded
            price: Execution price
        """
        title = f"{side.upper()} {symbol}"
        message = f"Executed {side} of {quantity} {symbol} at ${price:.2f}\nTotal: ${quantity * price:.2f}"
        
        self.send_alert(
            alert_type='trade',
            severity='medium',
            title=title,
            message=message,
            symbol=symbol
        )
    
    def send_stop_loss_alert(self, symbol: str, entry_price: float, 
                            exit_price: float, pnl: float):
        """Send alert for stop loss trigger.
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price
            exit_price: Exit price
            pnl: Profit/loss
        """
        pnl_pct = ((exit_price - entry_price) / entry_price) * 100
        
        title = f"STOP LOSS: {symbol}"
        message = f"""Stop loss triggered for {symbol}
        Entry: ${entry_price:.2f}
        Exit: ${exit_price:.2f}
        Loss: ${pnl:.2f} ({pnl_pct:.2f}%)
        """
        
        self.send_alert(
            alert_type='risk',
            severity='high',
            title=title,
            message=message,
            symbol=symbol
        )
    
    def send_take_profit_alert(self, symbol: str, entry_price: float, 
                              exit_price: float, pnl: float):
        """Send alert for take profit trigger.
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price
            exit_price: Exit price
            pnl: Profit/loss
        """
        pnl_pct = ((exit_price - entry_price) / entry_price) * 100
        
        title = f"TAKE PROFIT: {symbol}"
        message = f"""Take profit triggered for {symbol}
        Entry: ${entry_price:.2f}
        Exit: ${exit_price:.2f}
        Profit: ${pnl:.2f} ({pnl_pct:.2f}%)
        """
        
        self.send_alert(
            alert_type='trade',
            severity='low',
            title=title,
            message=message,
            symbol=symbol
        )
    
    def send_error_alert(self, error_message: str, context: str = None):
        """Send alert for errors.
        
        Args:
            error_message: Error message
            context: Additional context
        """
        title = "Trading Bot Error"
        message = f"Error: {error_message}"
        
        if context:
            message += f"\n\nContext: {context}"
        
        self.send_alert(
            alert_type='error',
            severity='critical',
            title=title,
            message=message
        )
    
    def send_daily_summary(self, stats: dict):
        """Send daily summary alert.
        
        Args:
            stats: Dictionary of daily statistics
        """
        title = f"Daily Summary - {datetime.now().strftime('%Y-%m-%d')}"
        message = f"""Daily Trading Summary
        
        Trades: {stats.get('trades_count', 0)}
        Win Rate: {stats.get('win_rate', 0):.1f}%
        P&L: ${stats.get('total_pnl', 0):.2f}
        
        Winning: {stats.get('winning_trades', 0)}
        Losing: {stats.get('losing_trades', 0)}
        """
        
        severity = 'low' if stats.get('total_pnl', 0) >= 0 else 'medium'
        
        self.send_alert(
            alert_type='info',
            severity=severity,
            title=title,
            message=message
        )


# Global instance
notifier = AlertNotifier()