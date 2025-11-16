# Phase 3: Infrastructure & Scaling

## Overview

Phase 3 adds production-ready infrastructure to the trading bot:

- **Database persistence** (SQLite/PostgreSQL)
- **Web dashboard** (React + Flask API)
- **Alert system** (Email + Webhooks)
- **Docker deployment**
- **Full trade history tracking**
- **Analytics and reporting**

## New Features

### 1. Database Layer

**Location**: `database/`

Trade history, positions, daily stats, alerts, and price data are now persisted in a database.

**Models**:
- `Trade`: All trade executions with P&L
- `Position`: Current open positions
- `DailyStats`: Aggregated daily metrics
- `Alert`: Notification history
- `PriceHistory`: Historical price data

**Usage**:
```python
from database.db_manager import db

# Initialize
db.init_db()

# Record trade
trade = db.record_trade('BTCUSD', 'buy', 0.001, 50000)

# Get recent trades
trades = db.get_recent_trades(limit=50)

# Update position
position = db.update_position('BTCUSD', 0.001, 50000, 51000)
```

### 2. Web Dashboard

**Location**: `dashboard/`

Real-time React dashboard for monitoring bot activity.

**Pages**:
- **Dashboard**: Overview with key metrics
- **Trades**: Complete trade history
- **Positions**: Open positions with live P&L
- **Analytics**: Charts and trends
- **Alerts**: Notification center

**Installation**:
```bash
cd dashboard
npm install
npm run dev
```

**Production Build**:
```bash
npm run build
```

### 3. Flask API

**Location**: `api/app.py`

REST API for dashboard and external integrations.

**Endpoints**:
- `GET /api/trades` - Get trade history
- `GET /api/positions` - Get open positions
- `GET /api/stats/summary` - Get summary statistics
- `GET /api/stats/daily` - Get daily stats
- `GET /api/alerts` - Get alerts
- `POST /api/alerts/{id}/acknowledge` - Acknowledge alert

**Run API**:
```bash
python api/app.py
```

API runs on http://localhost:5000

### 4. Alert System

**Location**: `alerts/notifier.py`

Multi-channel notification system.

**Channels**:
- **Email** (SMTP)
- **Webhooks** (Slack, Discord, custom)

**Alert Types**:
- Trade executions
- Stop loss triggers
- Take profit triggers
- Errors and warnings
- Daily summaries

**Configuration**:
```bash
# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=your_email@gmail.com

# Webhook
WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Usage**:
```python
from alerts.notifier import notifier

# Send trade alert
notifier.send_trade_alert('BTCUSD', 'buy', 0.001, 50000)

# Send stop loss alert
notifier.send_stop_loss_alert('BTCUSD', 50000, 47500, -2.5)

# Send error alert
notifier.send_error_alert("Connection failed", "Binance API")
```

### 5. Enhanced Trading Bot

**Location**: `trading_bot_integrated.py`

Fully integrated bot with all Phase 3 features.

**New Capabilities**:
- Automatic database recording
- Alert notifications
- Position tracking
- Daily stats updates
- Price history logging

**Run Bot**:
```bash
python trading_bot_integrated.py
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_phase3.txt
```

### 2. Configure Environment

```bash
cp .env.example.phase3 .env
# Edit .env with your credentials
```

### 3. Initialize Database

```python
from database.db_manager import db
db.init_db()
```

### 4. Start Components

**Terminal 1 - Trading Bot**:
```bash
python trading_bot_integrated.py
```

**Terminal 2 - API Server**:
```bash
python api/app.py
```

**Terminal 3 - Dashboard**:
```bash
cd dashboard
npm run dev
```

### 5. Access Dashboard

Open http://localhost:3000 in your browser

## Docker Deployment

### Build and Run

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Services

- **trading-bot**: Main trading bot
- **api**: Flask API server (port 5000)
- **dashboard**: React dashboard (port 3000)

### Data Persistence

Database and logs are stored in `./data` directory (Docker volume)

## Configuration

### Enhanced .env Variables

**New in Phase 3**:
```bash
# Database
DATABASE_URL=sqlite:///data/trading_bot.db

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_password
EMAIL_FROM=your_email
EMAIL_TO=your_email

# Webhook
WEBHOOK_URL=https://hooks.slack.com/...

# Dashboard
DASHBOARD_ENABLED=true
API_PORT=5000

# Alerts
ALERT_ON_TRADE=true
ALERT_ON_STOP_LOSS=true
ALERT_ON_TAKE_PROFIT=true
ALERT_ON_ERROR=true
DAILY_SUMMARY_ENABLED=true
```

## Database Schema

### Tables

1. **trades**: All trade executions
   - id, timestamp, symbol, side, quantity, price
   - status, execution_time, realized_pnl
   - strategy, notes

2. **positions**: Current open positions
   - symbol, quantity, average_entry_price
   - current_price, unrealized_pnl, is_open

3. **daily_stats**: Daily aggregated metrics
   - date, trades_count, win_rate
   - total_pnl, volume, max_drawdown

4. **alerts**: Notification history
   - type, severity, title, message
   - sent, acknowledged

5. **price_history**: Historical price data
   - symbol, timestamp, OHLCV
   - source

### Migrations

For schema changes:
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Production Deployment

### PostgreSQL Setup

1. **Install PostgreSQL**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql

# macOS
brew install postgresql
```

2. **Create Database**
```sql
CREATE DATABASE trading_bot;
CREATE USER trading_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE trading_bot TO trading_user;
```

3. **Update .env**
```bash
DATABASE_URL=postgresql://trading_user:secure_password@localhost:5432/trading_bot
```

### Email Setup (Gmail)

1. **Enable 2FA** on your Google account
2. **Generate App Password**:
   - Go to Google Account Settings
   - Security → 2-Step Verification
   - App passwords → Generate
3. **Use App Password** in .env (not regular password)

### Webhook Setup

**Slack**:
1. Create Slack app
2. Enable Incoming Webhooks
3. Copy webhook URL to .env

**Discord**:
1. Server Settings → Integrations
2. Create Webhook
3. Copy URL to .env

## Monitoring

### Logs

- **Bot logs**: `trading_bot.log`
- **Database logs**: Check SQLAlchemy echo
- **API logs**: Flask console output

### Health Checks

```bash
# API health
curl http://localhost:5000/api/health

# Check bot status
curl http://localhost:5000/api/bot/status
```

### Metrics

- **Dashboard**: Real-time metrics at http://localhost:3000
- **API**: Programmatic access via REST endpoints
- **Database**: Direct SQL queries for analysis

## Troubleshooting

### Database Issues

```python
# Reset database
from database.db_manager import db
from database.models import Base

Base.metadata.drop_all(db.engine)
db.init_db()
```

### Email Not Sending

1. Check SMTP credentials
2. Verify App Password (not regular password)
3. Check firewall/network settings
4. Test with Python:
```python
from alerts.notifier import notifier
notifier.send_alert('info', 'low', 'Test', 'Testing email')
```

### Dashboard Not Loading

1. Check API is running (port 5000)
2. Check CORS settings in Flask
3. Verify proxy configuration in `vite.config.js`
4. Check browser console for errors

## Performance

### Database Optimization

- Add indexes for frequently queried columns
- Use connection pooling
- Consider PostgreSQL for production
- Archive old data periodically

### API Optimization

- Enable caching for expensive queries
- Use pagination for large datasets
- Add rate limiting
- Use gunicorn workers

## Security

- **Never commit .env file**
- **Use strong passwords**
- **Enable HTTPS in production**
- **Restrict API access** (add authentication)
- **Regular security audits**
- **Keep dependencies updated**

## Next Steps

### Future Enhancements

- [ ] User authentication for dashboard
- [ ] Multi-user support
- [ ] Advanced charting (TradingView integration)
- [ ] Mobile app
- [ ] Telegram bot interface
- [ ] Machine learning predictions
- [ ] Portfolio optimization
- [ ] Options trading support

## Support

For issues:
1. Check logs
2. Review configuration
3. Test components individually
4. Open GitHub issue

---

**Phase 3 Complete!** 🎉

Your trading bot now has production-ready infrastructure with full monitoring, alerting, and web interface capabilities.