import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class MeanReversionStrategy:
    """
    Mean Reversion Trading Strategy based on Bollinger Bands
    """
    
    def __init__(self, ma_period=21, short_percentile=95, long_percentile=5):
        """
        Initialize the mean reversion strategy
        
        Args:
            ma_period (int): Moving average period
            short_percentile (int): Percentile for short position (sell signal)
            long_percentile (int): Percentile for long position (buy signal)
        """
        self.ma_period = ma_period
        self.short_percentile = short_percentile
        self.long_percentile = long_percentile
        self.positions = {}
        self.strategy_returns = {}
        self.buy_hold_returns = {}
        
    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate trading signals for a single stock
        
        Args:
            data (pd.DataFrame): Stock data with 'Close' or 'CLOSE' column
            
        Returns:
            pd.DataFrame: DataFrame with signals and positions
        """
        # Handle different column name formats
        close_col = None
        for col in ['Close', 'CLOSE', 'close']:
            if col in data.columns:
                close_col = col
                break
        
        if close_col is None:
            raise ValueError(f"No close price column found. Available columns: {list(data.columns)}")
        
        # Calculate log returns
        data['returns'] = np.log(data[close_col]).diff()
        
        # Calculate moving average
        data['ma'] = data[close_col].rolling(self.ma_period).mean()
        
        # Calculate ratio (price / moving average)
        data['ratio'] = data[close_col] / data['ma']
        
        # Calculate percentiles for signal generation
        percentiles = np.percentile(data['ratio'].dropna(), 
                                  [self.long_percentile, self.short_percentile])
        
        # Generate positions
        data['position'] = np.nan
        data.loc[data['ratio'] > percentiles[1], 'position'] = -1  # Short
        data.loc[data['ratio'] < percentiles[0], 'position'] = 1   # Long
        
        # Forward fill positions (hold until next signal)
        data['position'] = data['position'].ffill()
        
        # Calculate strategy returns
        data['strategy_return'] = data['returns'] * data['position'].shift(1)
        
        return data
    
    def backtest_single_stock(self, symbol: str, data: pd.DataFrame) -> Dict:
        """
        Backtest the strategy for a single stock
        
        Args:
            symbol (str): Stock symbol
            data (pd.DataFrame): Stock data
            
        Returns:
            Dict: Backtest results
        """
        # Calculate signals
        result_data = self.calculate_signals(data.copy())
        
        # Store positions and returns
        self.positions[symbol] = result_data['position']
        self.strategy_returns[symbol] = result_data['strategy_return']
        self.buy_hold_returns[symbol] = result_data['returns']
        
        # Calculate performance metrics
        strategy_cumulative = np.exp(result_data['strategy_return'].dropna()).cumprod()
        buy_hold_cumulative = np.exp(result_data['returns'].dropna()).cumprod()
        
        # Calculate metrics
        total_return_strategy = strategy_cumulative.iloc[-1] - 1
        total_return_buyhold = buy_hold_cumulative.iloc[-1] - 1
        
        volatility_strategy = result_data['strategy_return'].std() * np.sqrt(252)
        volatility_buyhold = result_data['returns'].std() * np.sqrt(252)
        
        sharpe_strategy = (result_data['strategy_return'].mean() * 252) / volatility_strategy
        sharpe_buyhold = (result_data['returns'].mean() * 252) / volatility_buyhold
        
        max_drawdown_strategy = self.calculate_max_drawdown(strategy_cumulative)
        max_drawdown_buyhold = self.calculate_max_drawdown(buy_hold_cumulative)
        
        return {
            'symbol': symbol,
            'strategy_return': total_return_strategy,
            'buyhold_return': total_return_buyhold,
            'strategy_volatility': volatility_strategy,
            'buyhold_volatility': volatility_buyhold,
            'strategy_sharpe': sharpe_strategy,
            'buyhold_sharpe': sharpe_buyhold,
            'strategy_max_drawdown': max_drawdown_strategy,
            'buyhold_max_drawdown': max_drawdown_buyhold,
            'excess_return': total_return_strategy - total_return_buyhold
        }
    
    def backtest_portfolio(self, stock_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Backtest the strategy for all stocks in the portfolio
        
        Args:
            stock_data (Dict): Dictionary with symbol as key and data as value
            
        Returns:
            pd.DataFrame: Portfolio backtest results
        """
        results = []
        
        for symbol, data in stock_data.items():
            print(f"Backtesting {symbol}...")
            result = self.backtest_single_stock(symbol, data)
            results.append(result)
            
        return pd.DataFrame(results)
    
    def calculate_portfolio_returns(self, equal_weighted=True) -> pd.DataFrame:
        """
        Calculate portfolio returns
        
        Args:
            equal_weighted (bool): Whether to use equal weights
            
        Returns:
            pd.DataFrame: Portfolio returns
        """
        if not self.strategy_returns:
            raise ValueError("No strategy returns available. Run backtest first.")
            
        # Combine all returns
        all_dates = set()
        for returns in self.strategy_returns.values():
            all_dates.update(returns.index)
            
        all_dates = sorted(list(all_dates))
        
        # Create portfolio returns DataFrame
        portfolio_returns = pd.DataFrame(index=all_dates)
        
        for symbol, returns in self.strategy_returns.items():
            portfolio_returns[symbol] = returns
            
        # Fill NaN values with 0
        portfolio_returns = portfolio_returns.fillna(0)
        
        if equal_weighted:
            # Equal weighted portfolio
            portfolio_returns['portfolio'] = portfolio_returns.mean(axis=1)
        else:
            # You can implement other weighting schemes here
            portfolio_returns['portfolio'] = portfolio_returns.mean(axis=1)
            
        return portfolio_returns
    
    def calculate_max_drawdown(self, cumulative_returns: pd.Series) -> float:
        """
        Calculate maximum drawdown
        
        Args:
            cumulative_returns (pd.Series): Cumulative returns series
            
        Returns:
            float: Maximum drawdown
        """
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        return drawdown.min()
    
    def plot_strategy_performance(self, symbol: str, data: pd.DataFrame):
        """
        Plot strategy performance for a single stock (COMMENTED OUT FOR NOW)
        
        Args:
            symbol (str): Stock symbol
            data (pd.DataFrame): Stock data with signals
        """
        print(f"Plotting functionality temporarily disabled for {symbol}")
        print("Use tabular output instead")
        
        # Ensure data has required columns by recalculating signals
        result_data = self.calculate_signals(data.copy())
        
        # Print basic statistics instead of plotting
        if not result_data.empty:
            print(f"\n{symbol} Strategy Summary:")
            print(f"Total data points: {len(result_data)}")
            print(f"Moving average period: {self.ma_period}")
            print(f"Price range: {result_data.iloc[:, 0].min():.2f} - {result_data.iloc[:, 0].max():.2f}")
            if 'strategy_return' in result_data.columns:
                total_strategy_return = np.exp(result_data['strategy_return'].dropna()).cumprod().iloc[-1] - 1
                total_buyhold_return = np.exp(result_data['returns'].dropna()).cumprod().iloc[-1] - 1
                print(f"Strategy return: {total_strategy_return:.2%}")
                print(f"Buy & hold return: {total_buyhold_return:.2%}")
        
        # Original plotting code commented out
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Handle different column name formats for plotting
        close_col = None
        for col in ['Close', 'CLOSE', 'close']:
            if col in data.columns:
                close_col = col
                break
        
        if close_col is None:
            print(f"Warning: No close price column found for {symbol}. Available columns: {list(data.columns)}")
            return
        
        # Plot 1: Price and Moving Average
        axes[0, 0].plot(data.index, data[close_col], label='Price', alpha=0.7)
        axes[0, 0].plot(data.index, data['ma'], label=f'{self.ma_period}-day MA', alpha=0.7)
        axes[0, 0].set_title(f'{symbol} - Price and Moving Average')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Plot 2: Ratio with percentiles
        axes[0, 1].plot(data.index, data['ratio'], label='Price/MA Ratio', alpha=0.7)
        percentiles = np.percentile(data['ratio'].dropna(), [self.long_percentile, self.short_percentile])
        axes[0, 1].axhline(percentiles[0], color='red', linestyle='--', alpha=0.7, label=f'{self.long_percentile}th percentile')
        axes[0, 1].axhline(percentiles[1], color='red', linestyle='--', alpha=0.7, label=f'{self.short_percentile}th percentile')
        axes[0, 1].set_title(f'{symbol} - Ratio and Signal Levels')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Plot 3: Positions
        axes[1, 0].plot(data.index, data['position'], label='Position', alpha=0.7)
        axes[1, 0].set_title(f'{symbol} - Trading Positions')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Plot 4: Cumulative Returns
        buy_hold_cum = np.exp(data['returns'].dropna()).cumprod()
        strategy_cum = np.exp(data['strategy_return'].dropna()).cumprod()
        
        axes[1, 1].plot(buy_hold_cum.index, buy_hold_cum, label='Buy & Hold', alpha=0.7)
        axes[1, 1].plot(strategy_cum.index, strategy_cum, label='Strategy', alpha=0.7)
        axes[1, 1].set_title(f'{symbol} - Cumulative Returns')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.show()
        """
    
    def generate_report(self, results: pd.DataFrame) -> str:
        """
        Generate a comprehensive report of the backtest results
        
        Args:
            results (pd.DataFrame): Backtest results
            
        Returns:
            str: Formatted report
        """
        report = "=" * 60 + "\n"
        report += "MEAN REVERSION STRATEGY BACKTEST REPORT\n"
        report += "=" * 60 + "\n\n"
        
        # Overall statistics
        avg_strategy_return = results['strategy_return'].mean()
        avg_buyhold_return = results['buyhold_return'].mean()
        avg_excess_return = results['excess_return'].mean()
        
        report += f"PORTFOLIO SUMMARY:\n"
        report += f"Average Strategy Return: {avg_strategy_return:.2%}\n"
        report += f"Average Buy & Hold Return: {avg_buyhold_return:.2%}\n"
        report += f"Average Excess Return: {avg_excess_return:.2%}\n"
        report += f"Number of Stocks: {len(results)}\n\n"
        
        # Top performers
        top_strategy = results.nlargest(5, 'strategy_return')
        report += "TOP 5 STRATEGY PERFORMERS:\n"
        for _, row in top_strategy.iterrows():
            report += f"{row['symbol']}: {row['strategy_return']:.2%}\n"
        report += "\n"
        
        # Worst performers
        worst_strategy = results.nsmallest(5, 'strategy_return')
        report += "BOTTOM 5 STRATEGY PERFORMERS:\n"
        for _, row in worst_strategy.iterrows():
            report += f"{row['symbol']}: {row['strategy_return']:.2%}\n"
        report += "\n"
        
        # Risk metrics
        report += "RISK METRICS:\n"
        report += f"Average Strategy Volatility: {results['strategy_volatility'].mean():.2%}\n"
        report += f"Average Buy & Hold Volatility: {results['buyhold_volatility'].mean():.2%}\n"
        report += f"Average Strategy Sharpe Ratio: {results['strategy_sharpe'].mean():.2f}\n"
        report += f"Average Buy & Hold Sharpe Ratio: {results['buyhold_sharpe'].mean():.2f}\n"
        report += f"Average Strategy Max Drawdown: {results['strategy_max_drawdown'].mean():.2%}\n"
        report += f"Average Buy & Hold Max Drawdown: {results['buyhold_max_drawdown'].mean():.2%}\n\n"
        
        # Win rate
        winning_stocks = len(results[results['excess_return'] > 0])
        total_stocks = len(results)
        win_rate = winning_stocks / total_stocks
        
        report += f"WIN RATE:\n"
        report += f"Stocks with positive excess return: {winning_stocks}/{total_stocks} ({win_rate:.1%})\n"
        
        return report 