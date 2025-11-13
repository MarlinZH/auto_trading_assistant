"""Portfolio analytics and performance metrics."""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PortfolioAnalytics:
    """Calculate portfolio performance metrics."""
    
    @staticmethod
    def calculate_returns(prices: pd.Series) -> pd.Series:
        """Calculate simple returns.
        
        Args:
            prices: Price series
            
        Returns:
            Returns series
        """
        return prices.pct_change()
    
    @staticmethod
    def calculate_log_returns(prices: pd.Series) -> pd.Series:
        """Calculate logarithmic returns.
        
        Args:
            prices: Price series
            
        Returns:
            Log returns series
        """
        return np.log(prices / prices.shift(1))
    
    @staticmethod
    def cumulative_returns(returns: pd.Series) -> pd.Series:
        """Calculate cumulative returns.
        
        Args:
            returns: Returns series
            
        Returns:
            Cumulative returns series
        """
        return (1 + returns).cumprod() - 1
    
    @staticmethod
    def sharpe_ratio(returns: pd.Series, 
                    risk_free_rate: float = 0.0,
                    periods: int = 252) -> float:
        """Calculate Sharpe ratio.
        
        Args:
            returns: Returns series
            risk_free_rate: Annual risk-free rate
            periods: Number of periods per year (252 for daily)
            
        Returns:
            Annualized Sharpe ratio
        """
        excess_returns = returns - risk_free_rate / periods
        if excess_returns.std() == 0:
            return 0.0
        return (excess_returns.mean() / excess_returns.std()) * np.sqrt(periods)
    
    @staticmethod
    def sortino_ratio(returns: pd.Series,
                     risk_free_rate: float = 0.0,
                     periods: int = 252) -> float:
        """Calculate Sortino ratio.
        
        Args:
            returns: Returns series
            risk_free_rate: Annual risk-free rate
            periods: Number of periods per year
            
        Returns:
            Annualized Sortino ratio
        """
        excess_returns = returns - risk_free_rate / periods
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        
        return (excess_returns.mean() / downside_returns.std()) * np.sqrt(periods)
    
    @staticmethod
    def max_drawdown(prices: pd.Series) -> Tuple[float, datetime, datetime]:
        """Calculate maximum drawdown.
        
        Args:
            prices: Price series
            
        Returns:
            Tuple of (max_drawdown, peak_date, trough_date)
        """
        cumulative = (prices / prices.iloc[0])
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        max_dd = drawdown.min()
        trough_date = drawdown.idxmin()
        
        # Find the peak before the trough
        peak_date = running_max[:trough_date].idxmax()
        
        return max_dd, peak_date, trough_date
    
    @staticmethod
    def calmar_ratio(returns: pd.Series, periods: int = 252) -> float:
        """Calculate Calmar ratio (return / max drawdown).
        
        Args:
            returns: Returns series
            periods: Number of periods per year
            
        Returns:
            Calmar ratio
        """
        cumulative_returns = PortfolioAnalytics.cumulative_returns(returns)
        prices = (1 + cumulative_returns)
        max_dd, _, _ = PortfolioAnalytics.max_drawdown(prices)
        
        if max_dd == 0:
            return 0.0
        
        annualized_return = returns.mean() * periods
        return annualized_return / abs(max_dd)
    
    @staticmethod
    def value_at_risk(returns: pd.Series, confidence: float = 0.95) -> float:
        """Calculate Value at Risk.
        
        Args:
            returns: Returns series
            confidence: Confidence level (0.95 = 95%)
            
        Returns:
            VaR value
        """
        return np.percentile(returns, (1 - confidence) * 100)
    
    @staticmethod
    def conditional_var(returns: pd.Series, confidence: float = 0.95) -> float:
        """Calculate Conditional VaR (Expected Shortfall).
        
        Args:
            returns: Returns series
            confidence: Confidence level
            
        Returns:
            CVaR value
        """
        var = PortfolioAnalytics.value_at_risk(returns, confidence)
        return returns[returns <= var].mean()
    
    @staticmethod
    def volatility(returns: pd.Series, periods: int = 252) -> float:
        """Calculate annualized volatility.
        
        Args:
            returns: Returns series
            periods: Number of periods per year
            
        Returns:
            Annualized volatility
        """
        return returns.std() * np.sqrt(periods)
    
    @staticmethod
    def beta(returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """Calculate portfolio beta relative to benchmark.
        
        Args:
            returns: Portfolio returns
            benchmark_returns: Benchmark returns
            
        Returns:
            Beta value
        """
        covariance = returns.cov(benchmark_returns)
        benchmark_variance = benchmark_returns.var()
        
        if benchmark_variance == 0:
            return 0.0
        
        return covariance / benchmark_variance
    
    @staticmethod
    def alpha(returns: pd.Series, 
             benchmark_returns: pd.Series,
             risk_free_rate: float = 0.0,
             periods: int = 252) -> float:
        """Calculate Jensen's alpha.
        
        Args:
            returns: Portfolio returns
            benchmark_returns: Benchmark returns
            risk_free_rate: Annual risk-free rate
            periods: Number of periods per year
            
        Returns:
            Alpha value
        """
        portfolio_return = returns.mean() * periods
        benchmark_return = benchmark_returns.mean() * periods
        beta = PortfolioAnalytics.beta(returns, benchmark_returns)
        
        expected_return = risk_free_rate + beta * (benchmark_return - risk_free_rate)
        return portfolio_return - expected_return
    
    @staticmethod
    def information_ratio(returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """Calculate information ratio.
        
        Args:
            returns: Portfolio returns
            benchmark_returns: Benchmark returns
            
        Returns:
            Information ratio
        """
        active_returns = returns - benchmark_returns
        tracking_error = active_returns.std()
        
        if tracking_error == 0:
            return 0.0
        
        return active_returns.mean() / tracking_error
    
    @staticmethod
    def win_rate(trades: List) -> float:
        """Calculate win rate from trades.
        
        Args:
            trades: List of Trade objects
            
        Returns:
            Win rate percentage
        """
        if not trades:
            return 0.0
        
        winning_trades = len([t for t in trades if t.pnl > 0])
        return (winning_trades / len(trades)) * 100
    
    @staticmethod
    def profit_factor(trades: List) -> float:
        """Calculate profit factor.
        
        Args:
            trades: List of Trade objects
            
        Returns:
            Profit factor
        """
        if not trades:
            return 0.0
        
        gross_profit = sum([t.pnl for t in trades if t.pnl > 0])
        gross_loss = abs(sum([t.pnl for t in trades if t.pnl < 0]))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss
    
    @staticmethod
    def generate_report(prices: pd.Series, 
                       returns: pd.Series,
                       trades: List = None,
                       benchmark_returns: pd.Series = None) -> Dict:
        """Generate comprehensive performance report.
        
        Args:
            prices: Price/equity series
            returns: Returns series
            trades: List of Trade objects (optional)
            benchmark_returns: Benchmark returns (optional)
            
        Returns:
            Dictionary with all metrics
        """
        report = {}
        
        # Basic returns
        total_return = (prices.iloc[-1] / prices.iloc[0]) - 1
        report['total_return'] = total_return * 100
        
        days = (prices.index[-1] - prices.index[0]).days
        years = days / 365.25
        report['annualized_return'] = (((1 + total_return) ** (1/years)) - 1) * 100 if years > 0 else 0
        
        # Risk metrics
        report['volatility'] = PortfolioAnalytics.volatility(returns) * 100
        report['sharpe_ratio'] = PortfolioAnalytics.sharpe_ratio(returns)
        report['sortino_ratio'] = PortfolioAnalytics.sortino_ratio(returns)
        
        max_dd, peak_date, trough_date = PortfolioAnalytics.max_drawdown(prices)
        report['max_drawdown'] = max_dd * 100
        report['max_drawdown_peak'] = peak_date
        report['max_drawdown_trough'] = trough_date
        
        report['calmar_ratio'] = PortfolioAnalytics.calmar_ratio(returns)
        report['var_95'] = PortfolioAnalytics.value_at_risk(returns) * 100
        report['cvar_95'] = PortfolioAnalytics.conditional_var(returns) * 100
        
        # Trade statistics
        if trades:
            report['total_trades'] = len(trades)
            report['win_rate'] = PortfolioAnalytics.win_rate(trades)
            report['profit_factor'] = PortfolioAnalytics.profit_factor(trades)
            
            winning_trades = [t.pnl for t in trades if t.pnl > 0]
            losing_trades = [t.pnl for t in trades if t.pnl < 0]
            
            report['avg_win'] = np.mean(winning_trades) if winning_trades else 0
            report['avg_loss'] = np.mean(losing_trades) if losing_trades else 0
            report['best_trade'] = max([t.pnl for t in trades]) if trades else 0
            report['worst_trade'] = min([t.pnl for t in trades]) if trades else 0
        
        # Benchmark comparison
        if benchmark_returns is not None:
            report['beta'] = PortfolioAnalytics.beta(returns, benchmark_returns)
            report['alpha'] = PortfolioAnalytics.alpha(returns, benchmark_returns) * 100
            report['information_ratio'] = PortfolioAnalytics.information_ratio(returns, benchmark_returns)
        
        return report
    
    @staticmethod
    def print_report(report: Dict) -> None:
        """Print formatted performance report.
        
        Args:
            report: Report dictionary from generate_report()
        """
        print("\n" + "="*60)
        print("PERFORMANCE REPORT")
        print("="*60)
        
        print("\nReturns:")
        print(f"  Total Return: {report['total_return']:.2f}%")
        print(f"  Annualized Return: {report['annualized_return']:.2f}%")
        
        print("\nRisk Metrics:")
        print(f"  Volatility: {report['volatility']:.2f}%")
        print(f"  Sharpe Ratio: {report['sharpe_ratio']:.2f}")
        print(f"  Sortino Ratio: {report['sortino_ratio']:.2f}")
        print(f"  Calmar Ratio: {report['calmar_ratio']:.2f}")
        print(f"  Max Drawdown: {report['max_drawdown']:.2f}%")
        print(f"  VaR (95%): {report['var_95']:.2f}%")
        print(f"  CVaR (95%): {report['cvar_95']:.2f}%")
        
        if 'total_trades' in report:
            print("\nTrade Statistics:")
            print(f"  Total Trades: {report['total_trades']}")
            print(f"  Win Rate: {report['win_rate']:.2f}%")
            print(f"  Profit Factor: {report['profit_factor']:.2f}")
            print(f"  Average Win: ${report['avg_win']:.2f}")
            print(f"  Average Loss: ${report['avg_loss']:.2f}")
            print(f"  Best Trade: ${report['best_trade']:.2f}")
            print(f"  Worst Trade: ${report['worst_trade']:.2f}")
        
        if 'beta' in report:
            print("\nBenchmark Comparison:")
            print(f"  Beta: {report['beta']:.2f}")
            print(f"  Alpha: {report['alpha']:.2f}%")
            print(f"  Information Ratio: {report['information_ratio']:.2f}")
        
        print("="*60 + "\n")