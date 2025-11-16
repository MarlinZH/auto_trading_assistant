"""Flask API for trading dashboard."""
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import logging

from database.db_manager import db
from database.models import TradeType, TradeStatus

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

logger = logging.getLogger(__name__)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})


# Trade endpoints
@app.route('/api/trades', methods=['GET'])
def get_trades():
    """Get trade history.
    
    Query params:
        limit: Number of trades (default: 50)
        symbol: Filter by symbol (optional)
        start_date: Start date filter (ISO format, optional)
        end_date: End date filter (ISO format, optional)
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        symbol = request.args.get('symbol')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if start_date_str and end_date_str:
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
            trades = db.get_trades_by_date_range(start_date, end_date, symbol)
        else:
            trades = db.get_recent_trades(limit, symbol)
        
        return jsonify([trade.to_dict() for trade in trades])
    
    except Exception as e:
        logger.error(f"Error fetching trades: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/trades/<int:trade_id>', methods=['GET'])
def get_trade(trade_id):
    """Get specific trade by ID."""
    try:
        with db.session_scope() as session:
            trade = session.query(db.Trade).filter(db.Trade.id == trade_id).first()
            if trade:
                return jsonify(trade.to_dict())
            return jsonify({'error': 'Trade not found'}), 404
    
    except Exception as e:
        logger.error(f"Error fetching trade: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Position endpoints
@app.route('/api/positions', methods=['GET'])
def get_positions():
    """Get all open positions."""
    try:
        positions = db.get_open_positions()
        return jsonify([pos.to_dict() for pos in positions])
    
    except Exception as e:
        logger.error(f"Error fetching positions: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/positions/<symbol>', methods=['GET'])
def get_position(symbol):
    """Get position for specific symbol."""
    try:
        position = db.get_position(symbol.upper())
        if position:
            return jsonify(position.to_dict())
        return jsonify({'error': 'Position not found'}), 404
    
    except Exception as e:
        logger.error(f"Error fetching position: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Statistics endpoints
@app.route('/api/stats/daily', methods=['GET'])
def get_daily_stats():
    """Get daily statistics.
    
    Query params:
        days: Number of days (default: 30)
    """
    try:
        days = request.args.get('days', 30, type=int)
        stats = db.get_daily_stats(days)
        return jsonify([stat.to_dict() for stat in stats])
    
    except Exception as e:
        logger.error(f"Error fetching daily stats: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats/summary', methods=['GET'])
def get_summary_stats():
    """Get overall summary statistics."""
    try:
        with db.session_scope() as session:
            # Total trades
            total_trades = session.query(db.Trade).filter(
                db.Trade.status == TradeStatus.EXECUTED
            ).count()
            
            # Calculate win rate
            winning_trades = session.query(db.Trade).filter(
                db.Trade.status == TradeStatus.EXECUTED,
                db.Trade.realized_pnl > 0
            ).count()
            
            losing_trades = session.query(db.Trade).filter(
                db.Trade.status == TradeStatus.EXECUTED,
                db.Trade.realized_pnl < 0
            ).count()
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Total P&L
            total_pnl = session.query(db.func.sum(db.Trade.realized_pnl)).filter(
                db.Trade.status == TradeStatus.EXECUTED
            ).scalar() or 0
            
            # Open positions value
            positions = db.get_open_positions()
            open_position_value = sum(pos.quantity * pos.current_price for pos in positions if pos.current_price)
            unrealized_pnl = sum(pos.unrealized_pnl for pos in positions if pos.unrealized_pnl)
            
            return jsonify({
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': round(win_rate, 2),
                'total_realized_pnl': round(total_pnl, 2),
                'unrealized_pnl': round(unrealized_pnl, 2),
                'total_pnl': round(total_pnl + unrealized_pnl, 2),
                'open_positions_count': len(positions),
                'open_position_value': round(open_position_value, 2)
            })
    
    except Exception as e:
        logger.error(f"Error calculating summary stats: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Alert endpoints
@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get alerts.
    
    Query params:
        severity: Filter by severity (optional)
        acknowledged: Filter by acknowledgment status (optional)
    """
    try:
        severity = request.args.get('severity')
        acknowledged = request.args.get('acknowledged', type=bool)
        
        with db.session_scope() as session:
            query = session.query(db.Alert)
            
            if severity:
                query = query.filter(db.Alert.severity == severity)
            
            if acknowledged is not None:
                query = query.filter(db.Alert.acknowledged == acknowledged)
            
            alerts = query.order_by(db.Alert.timestamp.desc()).limit(100).all()
            return jsonify([alert.to_dict() for alert in alerts])
    
    except Exception as e:
        logger.error(f"Error fetching alerts: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge an alert."""
    try:
        db.acknowledge_alert(alert_id)
        return jsonify({'success': True, 'message': 'Alert acknowledged'})
    
    except Exception as e:
        logger.error(f"Error acknowledging alert: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Price history endpoints
@app.route('/api/prices/<symbol>', methods=['GET'])
def get_price_history(symbol):
    """Get price history for symbol.
    
    Query params:
        start_date: Start date (ISO format, required)
        end_date: End date (ISO format, optional)
    """
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str:
            return jsonify({'error': 'start_date is required'}), 400
        
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
        
        prices = db.get_price_history(symbol.upper(), start_date, end_date)
        return jsonify([price.to_dict() for price in prices])
    
    except Exception as e:
        logger.error(f"Error fetching price history: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Bot status endpoint
@app.route('/api/bot/status', methods=['GET'])
def get_bot_status():
    """Get trading bot status."""
    # This would be integrated with the actual bot
    # For now, return mock data
    return jsonify({
        'running': True,
        'uptime': '2 hours 34 minutes',
        'last_trade': '10 minutes ago',
        'paper_trading': True,
        'strategy': 'momentum',
        'check_interval': 60
    })


if __name__ == '__main__':
    # Initialize database
    db.init_db()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)