"""Backtesting framework for trading strategies."""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Callable, Optional, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class BacktestConfig:
    """Configuration for backtesting."""
    initial_capital: float = 10000.0
    commission: float = 0.001  # 0.1% per trade
    slippage: float = 0.0005  # 0.05% slippage
    position_size: float = 1.0  # Fraction of capital per trade (0-1)
    stop_loss: Optional[float] = None  # Stop loss percentage
    take_profit: Optional[float] = None  # Take profit percentage
    max_positions: int = 1  # Maximum concurrent positions


@dataclass
class Trade:
    """Record of a single trade."""
    entry_date: datetime
    exit_date: Optional[datetime] = None
    entry_price: float = 0.0
    exit_price: float = 0.0
    quantity: float = 0.0
    side: str = 'long'  # 'long' or 'short'
    pnl: float = 0.0
    pnl_percent: float = 0.0
    commission: float = 0.0
    exit_reason: str = ''  # 'signal', 'stop_loss', 'take_profit'


@dataclass
class BacktestResults:
    """Results from a backtest run."""
    trades: List[Trade] = field(default_factory=list)
    equity_curve: pd.Series = field(default_factory=pd.Series)
    
    # Performance metrics
    total_return: float = 0.0
    total_return_pct: float = 0.0
    annualized_return: float = 0.0
    
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    
    best_trade: float = 0.0
    worst_trade: float = 0.0
    avg_trade_duration: float = 0.0
    
    def __str__(self) -> str:
        """String representation of results."""
        return f"""
Backtest Results:
{'='*50}
Performance:
  Total Return: ${self.total_return:,.2f} ({self.total_return_pct:.2f}%)
  Annualized Return: {self.annualized_return:.2f}%
  Sharpe Ratio: {self.sharpe_ratio:.2f}
  Sortino Ratio: {self.sortino_ratio:.2f}
  Max Drawdown: ${self.max_drawdown:,.2f} ({self.max_drawdown_pct:.2f}%)

Trades:
  Total: {self.total_trades}
  Winners: {self.winning_trades} ({self.win_rate:.2f}%)
  Losers: {self.losing_trades}
  
Trade Statistics:
  Average Win: ${self.avg_win:,.2f}
  Average Loss: ${self.avg_loss:,.2f}
  Profit Factor: {self.profit_factor:.2f}
  Best Trade: ${self.best_trade:,.2f}
  Worst Trade: ${self.worst_trade:,.2f}
  Avg Duration: {self.avg_trade_duration:.1f} periods
{'='*50}
"""


class Backtester:
    """Backtest trading strategies on historical data."""
    
    def __init__(self, config: BacktestConfig = None):
        """Initialize backtester.
        
        Args:
            config: Backtest configuration
        """
        self.config = config or BacktestConfig()
        self.trades: List[Trade] = []
        self.current_position: Optional[Trade] = None
        self.capital = self.config.initial_capital
        self.equity_history: List[float] = []
        
    def run(self, 
            data: pd.DataFrame, 
            signals: pd.Series,
            price_col: str = 'close') -> BacktestResults:
        """Run backtest on historical data.
        
        Args:
            data: OHLCV data with DatetimeIndex
            signals: Trading signals (1=buy, -1=sell, 0=hold)
            price_col: Column name for entry/exit prices
            
        Returns:
            BacktestResults object
        """
        logger.info(f"Starting backtest with {len(data)} data points")
        logger.info(f"Initial capital: ${self.config.initial_capital:,.2f}")
        
        # Reset state
        self.trades = []
        self.current_position = None
        self.capital = self.config.initial_capital
        self.equity_history = [self.capital]
        
        # Align signals with data
        signals = signals.reindex(data.index, fill_value=0)
        
        # Iterate through data
        for idx, (date, row) in enumerate(data.iterrows()):
            price = row[price_col]
            signal = signals.loc[date]
            
            # Update equity
            current_equity = self._calculate_equity(price)
            self.equity_history.append(current_equity)
            
            # Check stop loss / take profit
            if self.current_position:
                exit_reason = self._check_exit_conditions(price)
                if exit_reason:
                    self._exit_position(date, price, exit_reason)
                    continue
            
            # Process signals
            if signal == 1 and not self.current_position:
                # Buy signal - open long position
                self._enter_position(date, price, 'long')
                
            elif signal == -1 and self.current_position:
                # Sell signal - close position
                self._exit_position(date, price, 'signal')
        
        # Close any open positions at end
        if self.current_position:
            final_price = data.iloc[-1][price_col]
            final_date = data.index[-1]
            self._exit_position(final_date, final_price, 'end_of_data')
        
        # Calculate and return results
        results = self._calculate_results(data.index)
        
        logger.info(f"Backtest complete: {results.total_trades} trades")
        logger.info(f"Final equity: ${results.equity_curve.iloc[-1]:,.2f}")
        
        return results
    
    def _enter_position(self, date: datetime, price: float, side: str) -> None:
        """Open a new position."""
        if len([t for t in self.trades if t.exit_date is None]) >= self.config.max_positions:
            return  # Max positions reached
        
        # Calculate position size
        position_value = self.capital * self.config.position_size
        commission_cost = position_value * self.config.commission
        slippage_cost = position_value * self.config.slippage
        
        # Adjust for slippage
        effective_price = price * (1 + self.config.slippage) if side == 'long' else price * (1 - self.config.slippage)
        
        quantity = (position_value - commission_cost - slippage_cost) / effective_price
        
        if quantity <= 0:
            return  # Not enough capital
        
        trade = Trade(
            entry_date=date,
            entry_price=effective_price,
            quantity=quantity,
            side=side,
            commission=commission_cost
        )
        
        self.current_position = trade
        self.capital -= (quantity * effective_price + commission_cost + slippage_cost)
        
        logger.debug(f"Opened {side} position: {quantity:.4f} @ ${effective_price:.2f}")
    
    def _exit_position(self, date: datetime, price: float, reason: str) -> None:
        """Close current position."""
        if not self.current_position:
            return
        
        trade = self.current_position
        
        # Adjust for slippage
        effective_price = price * (1 - self.config.slippage) if trade.side == 'long' else price * (1 + self.config.slippage)
        
        # Calculate P&L
        if trade.side == 'long':
            pnl = (effective_price - trade.entry_price) * trade.quantity
        else:
            pnl = (trade.entry_price - effective_price) * trade.quantity
        
        commission_cost = (trade.quantity * effective_price) * self.config.commission
        pnl -= (trade.commission + commission_cost)
        
        # Update trade record
        trade.exit_date = date
        trade.exit_price = effective_price
        trade.pnl = pnl
        trade.pnl_percent = (pnl / (trade.entry_price * trade.quantity)) * 100
        trade.commission += commission_cost
        trade.exit_reason = reason
        
        # Update capital
        self.capital += (trade.quantity * effective_price + pnl - commission_cost)
        
        # Record trade
        self.trades.append(trade)
        self.current_position = None
        
        logger.debug(f"Closed position: P&L ${pnl:.2f} ({trade.pnl_percent:.2f}%) - {reason}")
    
    def _check_exit_conditions(self, current_price: float) -> Optional[str]:
        """Check if stop loss or take profit triggered."""
        if not self.current_position:
            return None
        
        trade = self.current_position
        
        # Calculate P&L percentage
        if trade.side == 'long':
            pnl_pct = ((current_price - trade.entry_price) / trade.entry_price) * 100
        else:
            pnl_pct = ((trade.entry_price - current_price) / trade.entry_price) * 100
        
        # Check stop loss
        if self.config.stop_loss and pnl_pct <= -self.config.stop_loss:
            return 'stop_loss'
        
        # Check take profit
        if self.config.take_profit and pnl_pct >= self.config.take_profit:
            return 'take_profit'
        
        return None
    
    def _calculate_equity(self, current_price: float) -> float:
        """Calculate current total equity."""
        equity = self.capital
        
        if self.current_position:
            trade = self.current_position
            if trade.side == 'long':
                position_value = trade.quantity * current_price
            else:
                position_value = trade.quantity * (2 * trade.entry_price - current_price)
            equity += position_value
        
        return equity
    
    def _calculate_results(self, dates: pd.DatetimeIndex) -> BacktestResults:
        """Calculate performance metrics."""
        results = BacktestResults()
        results.trades = self.trades
        
        # Create equity curve
        results.equity_curve = pd.Series(self.equity_history, index=dates)
        
        if not self.trades:
            return results
        
        # Basic metrics
        results.total_trades = len(self.trades)
        results.winning_trades = len([t for t in self.trades if t.pnl > 0])
        results.losing_trades = len([t for t in self.trades if t.pnl < 0])
        results.win_rate = (results.winning_trades / results.total_trades) * 100 if results.total_trades > 0 else 0
        
        # Return metrics
        final_equity = self.equity_history[-1]
        results.total_return = final_equity - self.config.initial_capital
        results.total_return_pct = (results.total_return / self.config.initial_capital) * 100
        
        # Annualized return
        days = (dates[-1] - dates[0]).days
        years = days / 365.25
        if years > 0:
            results.annualized_return = (((final_equity / self.config.initial_capital) ** (1/years)) - 1) * 100
        
        # Trade statistics
        winning_trades = [t.pnl for t in self.trades if t.pnl > 0]
        losing_trades = [t.pnl for t in self.trades if t.pnl < 0]
        
        results.avg_win = np.mean(winning_trades) if winning_trades else 0
        results.avg_loss = np.mean(losing_trades) if losing_trades else 0
        results.best_trade = max([t.pnl for t in self.trades]) if self.trades else 0
        results.worst_trade = min([t.pnl for t in self.trades]) if self.trades else 0
        
        # Profit factor
        gross_profit = sum(winning_trades) if winning_trades else 0
        gross_loss = abs(sum(losing_trades)) if losing_trades else 0
        results.profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Average trade duration
        durations = [(t.exit_date - t.entry_date).total_seconds() / 3600 for t in self.trades if t.exit_date]
        results.avg_trade_duration = np.mean(durations) if durations else 0
        
        # Risk metrics
        returns = results.equity_curve.pct_change().dropna()
        
        if len(returns) > 0:
            # Sharpe ratio (assuming 0% risk-free rate)
            results.sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
            
            # Sortino ratio
            downside_returns = returns[returns < 0]
            downside_std = downside_returns.std() if len(downside_returns) > 0 else 0
            results.sortino_ratio = (returns.mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0
        
        # Maximum drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        results.max_drawdown_pct = drawdown.min() * 100
        results.max_drawdown = (results.equity_curve.max() - results.equity_curve[drawdown.idxmin()]) if len(drawdown) > 0 else 0
        
        return results


def load_historical_data(symbol: str, 
                        start_date: str, 
                        end_date: str,
                        source: str = 'yfinance') -> pd.DataFrame:
    """Load historical OHLCV data.
    
    Args:
        symbol: Trading symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        source: Data source ('yfinance', 'binance', 'csv')
        
    Returns:
        DataFrame with OHLCV data
    """
    if source == 'yfinance':
        try:
            import yfinance as yf
            data = yf.download(symbol, start=start_date, end=end_date, progress=False)
            data.columns = data.columns.str.lower()
            return data
        except ImportError:
            logger.error("yfinance not installed. Install with: pip install yfinance")
            raise
    
    elif source == 'binance':
        # Placeholder for Binance historical data
        logger.warning("Binance historical data not yet implemented")
        return pd.DataFrame()
    
    elif source == 'csv':
        data = pd.read_csv(symbol, index_col=0, parse_dates=True)
        return data
    
    else:
        raise ValueError(f"Unknown data source: {source}")