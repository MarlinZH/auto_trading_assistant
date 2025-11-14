"""Backtesting engine for testing trading strategies on historical data."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """Record of a single trade."""
    timestamp: datetime
    symbol: str
    side: str  # 'buy' or 'sell'
    price: float
    quantity: float
    commission: float = 0.0
    
    @property
    def value(self) -> float:
        """Total trade value."""
        return self.price * self.quantity


@dataclass
class Position:
    """Current position state."""
    symbol: str
    quantity: float = 0.0
    entry_price: float = 0.0
    entry_time: Optional[datetime] = None
    
    @property
    def is_open(self) -> bool:
        """Check if position is currently open."""
        return self.quantity > 0
    
    def unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized profit/loss."""
        if not self.is_open:
            return 0.0
        return (current_price - self.entry_price) * self.quantity
    
    def unrealized_pnl_pct(self, current_price: float) -> float:
        """Calculate unrealized profit/loss percentage."""
        if not self.is_open or self.entry_price == 0:
            return 0.0
        return ((current_price - self.entry_price) / self.entry_price) * 100


@dataclass
class BacktestResult:
    """Results from a backtest run."""
    # Basic metrics
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    
    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    # Performance metrics
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_pct: float
    
    # Profit metrics
    total_profit: float
    total_loss: float
    average_profit: float
    average_loss: float
    profit_factor: float
    
    # Time metrics
    start_date: datetime
    end_date: datetime
    duration_days: int
    
    # Detailed records
    trades: List[Trade] = field(default_factory=list)
    equity_curve: pd.Series = field(default_factory=pd.Series)
    
    def summary(self) -> str:
        """Generate a summary report."""
        return f"""
╔══════════════════════════════════════════════════════════╗
║              BACKTEST RESULTS SUMMARY                    ║
╠══════════════════════════════════════════════════════════╣
║ Period: {self.start_date.date()} to {self.end_date.date()}
║ Duration: {self.duration_days} days
║
║ CAPITAL
║ Initial: ${self.initial_capital:,.2f}
║ Final:   ${self.final_capital:,.2f}
║ Return:  ${self.total_return:,.2f} ({self.total_return_pct:.2f}%)
║
║ TRADES
║ Total:   {self.total_trades}
║ Wins:    {self.winning_trades} ({self.win_rate:.1f}%)
║ Losses:  {self.losing_trades}
║
║ PERFORMANCE
║ Sharpe Ratio:    {self.sharpe_ratio:.2f}
║ Max Drawdown:    ${self.max_drawdown:,.2f} ({self.max_drawdown_pct:.2f}%)
║ Profit Factor:   {self.profit_factor:.2f}
║
║ PROFIT/LOSS
║ Total Profit:    ${self.total_profit:,.2f}
║ Total Loss:      ${self.total_loss:,.2f}
║ Avg Win:         ${self.average_profit:,.2f}
║ Avg Loss:        ${self.average_loss:,.2f}
╚══════════════════════════════════════════════════════════╝
        """


class BacktestEngine:
    """Engine for backtesting trading strategies."""
    
    def __init__(self, 
                 initial_capital: float = 10000.0,
                 commission: float = 0.001):
        """
        Initialize backtest engine.
        
        Args:
            initial_capital: Starting capital
            commission: Commission rate per trade (e.g., 0.001 = 0.1%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        
        # State variables
        self.capital = initial_capital
        self.position = Position(symbol="")
        self.trades: List[Trade] = []
        self.equity_history: List[Tuple[datetime, float]] = []
        
    def reset(self):
        """Reset the engine to initial state."""
        self.capital = self.initial_capital
        self.position = Position(symbol="")
        self.trades = []
        self.equity_history = []
    
    def buy(self, timestamp: datetime, symbol: str, price: float, quantity: float) -> bool:
        """Execute a buy order."""
        cost = price * quantity
        commission_cost = cost * self.commission
        total_cost = cost + commission_cost
        
        if total_cost > self.capital:
            logger.warning(f"Insufficient capital for buy: need ${total_cost:.2f}, have ${self.capital:.2f}")
            return False
        
        # Execute trade
        self.capital -= total_cost
        self.position.symbol = symbol
        self.position.quantity += quantity
        self.position.entry_price = price
        self.position.entry_time = timestamp
        
        trade = Trade(
            timestamp=timestamp,
            symbol=symbol,
            side='buy',
            price=price,
            quantity=quantity,
            commission=commission_cost
        )
        self.trades.append(trade)
        
        logger.debug(f"BUY: {quantity} {symbol} @ ${price:.2f} (Commission: ${commission_cost:.2f})")
        return True
    
    def sell(self, timestamp: datetime, symbol: str, price: float, quantity: float) -> bool:
        """Execute a sell order."""
        if not self.position.is_open or self.position.quantity < quantity:
            logger.warning(f"Insufficient position to sell: have {self.position.quantity}, trying to sell {quantity}")
            return False
        
        # Calculate proceeds
        proceeds = price * quantity
        commission_cost = proceeds * self.commission
        net_proceeds = proceeds - commission_cost
        
        # Execute trade
        self.capital += net_proceeds
        self.position.quantity -= quantity
        
        if self.position.quantity == 0:
            self.position = Position(symbol="")
        
        trade = Trade(
            timestamp=timestamp,
            symbol=symbol,
            side='sell',
            price=price,
            quantity=quantity,
            commission=commission_cost
        )
        self.trades.append(trade)
        
        logger.debug(f"SELL: {quantity} {symbol} @ ${price:.2f} (Commission: ${commission_cost:.2f})")
        return True
    
    def get_portfolio_value(self, current_price: float) -> float:
        """Get current total portfolio value."""
        position_value = self.position.quantity * current_price if self.position.is_open else 0
        return self.capital + position_value
    
    def run(self, 
            data: pd.DataFrame,
            strategy: Callable[[pd.DataFrame, int, 'BacktestEngine'], None]) -> BacktestResult:
        """
        Run backtest with given strategy.
        
        Args:
            data: DataFrame with OHLCV data (datetime index, columns: open, high, low, close, volume)
            strategy: Strategy function that takes (data, current_index, engine) and executes trades
        
        Returns:
            BacktestResult with performance metrics
        """
        self.reset()
        
        logger.info(f"Starting backtest with ${self.initial_capital:,.2f}")
        logger.info(f"Data period: {data.index[0]} to {data.index[-1]}")
        logger.info(f"Total bars: {len(data)}")
        
        # Run strategy on each bar
        for i in range(len(data)):
            timestamp = data.index[i]
            current_price = data['close'].iloc[i]
            
            # Execute strategy
            strategy(data, i, self)
            
            # Record equity
            equity = self.get_portfolio_value(current_price)
            self.equity_history.append((timestamp, equity))
        
        # Calculate results
        return self._calculate_results(data)
    
    def _calculate_results(self, data: pd.DataFrame) -> BacktestResult:
        """Calculate backtest performance metrics."""
        # Basic metrics
        final_price = data['close'].iloc[-1]
        final_capital = self.get_portfolio_value(final_price)
        total_return = final_capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        # Trade statistics
        winning_trades = []
        losing_trades = []
        
        for i in range(0, len(self.trades) - 1, 2):
            if i + 1 < len(self.trades):
                buy_trade = self.trades[i]
                sell_trade = self.trades[i + 1]
                
                if buy_trade.side == 'buy' and sell_trade.side == 'sell':
                    pnl = (sell_trade.price - buy_trade.price) * buy_trade.quantity
                    pnl -= (buy_trade.commission + sell_trade.commission)
                    
                    if pnl > 0:
                        winning_trades.append(pnl)
                    else:
                        losing_trades.append(abs(pnl))
        
        total_trades = len(winning_trades) + len(losing_trades)
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        
        total_profit = sum(winning_trades)
        total_loss = sum(losing_trades)
        average_profit = np.mean(winning_trades) if winning_trades else 0
        average_loss = np.mean(losing_trades) if losing_trades else 0
        profit_factor = (total_profit / total_loss) if total_loss > 0 else 0
        
        # Equity curve
        equity_df = pd.DataFrame(self.equity_history, columns=['timestamp', 'equity'])
        equity_df.set_index('timestamp', inplace=True)
        equity_curve = equity_df['equity']
        
        # Drawdown
        running_max = equity_curve.expanding().max()
        drawdown = equity_curve - running_max
        max_drawdown = drawdown.min()
        max_drawdown_pct = (max_drawdown / running_max.max() * 100) if running_max.max() > 0 else 0
        
        # Sharpe ratio (annualized, assuming daily data)
        returns = equity_curve.pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std() * np.sqrt(252)) if len(returns) > 0 and returns.std() > 0 else 0
        
        # Time metrics
        start_date = data.index[0]
        end_date = data.index[-1]
        duration_days = (end_date - start_date).days
        
        result = BacktestResult(
            initial_capital=self.initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            total_return_pct=total_return_pct,
            total_trades=total_trades,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_pct=max_drawdown_pct,
            total_profit=total_profit,
            total_loss=total_loss,
            average_profit=average_profit,
            average_loss=average_loss,
            profit_factor=profit_factor,
            start_date=start_date,
            end_date=end_date,
            duration_days=duration_days,
            trades=self.trades,
            equity_curve=equity_curve
        )
        
        logger.info("Backtest complete")
        logger.info(result.summary())
        
        return result