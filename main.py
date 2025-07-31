#!/usr/bin/env python3
"""
Main execution file for Nifty 50 Mean Reversion Trading Algorithm
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Import our custom modules
import config.config as cfg
from src.data_loader_async import AsyncDataLoader
from src.mean_reversion_strategy import MeanReversionStrategy

def main():
    """
    Main function to run the mean reversion trading algorithm
    """
    print("=" * 60)
    print("NIFTY 50 MEAN REVERSION TRADING ALGORITHM")
    print("=" * 60)
    print()
    
    # Step 1: Load data
    print("Step 1: Loading Nifty 50 stock data...")
    
    # Check if Dhan credentials are available
    try:
        from config.dhan_config import DHAN_CLIENT_CODE, DHAN_TOKEN_ID
        client_code = DHAN_CLIENT_CODE
        token_id = DHAN_TOKEN_ID
    except ImportError:
        print("Dhan credentials not found. Please configure config/dhan_config.py")
        return
    
    data_loader = AsyncDataLoader(
        symbols=cfg.NIFTY_50_SYMBOLS,
        start_date=cfg.START_DATE,
        end_date=cfg.END_DATE,
        client_code=client_code,
        token_id=token_id,
        debug=True,  # Enable debug mode to see data structure
        max_workers=3  # Use conservative worker count for rate limiting
    )
    
    # Fetch all stock data using batch processing (recommended for rate limiting)
    print("Using batch processing to respect API rate limits...")
    stock_data = data_loader.fetch_all_data_batch(batch_size=3)
    
    if not stock_data:
        print("No data fetched. Exiting...")
        return
    
    print(f"Successfully loaded data for {len(stock_data)} stocks")
    print()
    
    # Step 2: Initialize strategy
    print("Step 2: Initializing mean reversion strategy...")
    strategy = MeanReversionStrategy(
        ma_period=cfg.MOVING_AVERAGE_PERIOD,
        short_percentile=cfg.SHORT_PERCENTILE,
        long_percentile=cfg.LONG_PERCENTILE
    )
    print(f"Strategy parameters:")
    print(f"  - Moving Average Period: {cfg.MOVING_AVERAGE_PERIOD}")
    print(f"  - Short Signal Percentile: {cfg.SHORT_PERCENTILE}")
    print(f"  - Long Signal Percentile: {cfg.LONG_PERCENTILE}")
    print()
    
    # Step 3: Run backtest
    print("Step 3: Running backtest...")
    results = strategy.backtest_portfolio(stock_data)
    print("Backtest completed!")
    print()
    
    # Step 4: Generate and display results
    print("Step 4: Analyzing results...")
    
    # Display summary statistics
    print("SUMMARY STATISTICS:")
    print(f"Number of stocks analyzed: {len(results)}")
    print(f"Average strategy return: {results['strategy_return'].mean():.2%}")
    print(f"Average buy & hold return: {results['buyhold_return'].mean():.2%}")
    print(f"Average excess return: {results['excess_return'].mean():.2%}")
    print()
    
    # Generate detailed report
    report = strategy.generate_report(results)
    print(report)
    
    # Step 5: Create simple tabular output
    print("Step 5: Creating tabular summary...")
    create_tabular_output(results)
    
    # Step 6: Save results
    print("Step 6: Saving results...")
    save_results(results, strategy)
    
    print("=" * 60)
    print("ANALYSIS COMPLETE!")
    print("=" * 60)

def create_tabular_output(results):
    """
    Create simple tabular output instead of charts
    """
    print("\n" + "=" * 80)
    print("DETAILED RESULTS SUMMARY")
    print("=" * 80)
    
    # Sort by strategy return
    results_sorted = results.sort_values('strategy_return', ascending=False)
    
    # Display top performers
    print("\nTOP 10 PERFORMERS:")
    print("-" * 80)
    print(f"{'Rank':<4} {'Symbol':<12} {'Strategy':<10} {'Buy&Hold':<10} {'Excess':<10} {'Sharpe':<8}")
    print("-" * 80)
    
    for i, (_, row) in enumerate(results_sorted.head(10).iterrows(), 1):
        print(f"{i:<4} {row['symbol']:<12} {row['strategy_return']:>8.2%} "
              f"{row['buyhold_return']:>8.2%} {row['excess_return']:>8.2%} "
              f"{row['strategy_sharpe']:>6.2f}")
    
    # Display bottom performers
    print("\nBOTTOM 10 PERFORMERS:")
    print("-" * 80)
    print(f"{'Rank':<4} {'Symbol':<12} {'Strategy':<10} {'Buy&Hold':<10} {'Excess':<10} {'Sharpe':<8}")
    print("-" * 80)
    
    for i, (_, row) in enumerate(results_sorted.tail(10).iterrows(), 1):
        print(f"{i:<4} {row['symbol']:<12} {row['strategy_return']:>8.2%} "
              f"{row['buyhold_return']:>8.2%} {row['excess_return']:>8.2%} "
              f"{row['strategy_sharpe']:>6.2f}")
    
    # Summary statistics table
    print("\nSUMMARY STATISTICS:")
    print("-" * 60)
    print(f"{'Metric':<25} {'Strategy':<12} {'Buy & Hold':<12}")
    print("-" * 60)
    print(f"{'Mean Return':<25} {results['strategy_return'].mean():>10.2%} {results['buyhold_return'].mean():>10.2%}")
    print(f"{'Median Return':<25} {results['strategy_return'].median():>10.2%} {results['buyhold_return'].median():>10.2%}")
    print(f"{'Std Deviation':<25} {results['strategy_return'].std():>10.2%} {results['buyhold_return'].std():>10.2%}")
    print(f"{'Min Return':<25} {results['strategy_return'].min():>10.2%} {results['buyhold_return'].min():>10.2%}")
    print(f"{'Max Return':<25} {results['strategy_return'].max():>10.2%} {results['buyhold_return'].max():>10.2%}")
    print(f"{'Mean Sharpe Ratio':<25} {results['strategy_sharpe'].mean():>10.2f} {results['buyhold_sharpe'].mean():>10.2f}")
    
    # Win rate analysis
    positive_excess = (results['excess_return'] > 0).sum()
    total_stocks = len(results)
    win_rate = positive_excess / total_stocks * 100
    
    print(f"\nWIN RATE ANALYSIS:")
    print("-" * 40)
    print(f"Stocks with positive excess return: {positive_excess}/{total_stocks} ({win_rate:.1f}%)")
    print(f"Mean excess return: {results['excess_return'].mean():.2%}")
    print(f"Median excess return: {results['excess_return'].median():.2%}")
    
    # Risk metrics
    print(f"\nRISK METRICS:")
    print("-" * 40)
    print(f"Mean Strategy Volatility: {results['strategy_volatility'].mean():.2%}")
    print(f"Mean Buy&Hold Volatility: {results['buyhold_volatility'].mean():.2%}")
    print(f"Mean Strategy Max Drawdown: {results['strategy_max_drawdown'].mean():.2%}")
    print(f"Mean Buy&Hold Max Drawdown: {results['buyhold_max_drawdown'].mean():.2%}")

# Commented out visualization functions for now
"""
def create_visualizations(results, strategy, stock_data):
    # Visualization code commented out - keeping for future use
    pass
"""

def save_results(results, strategy):
    """
    Save results to files
    """
    # Create data directory for results
    os.makedirs('data/results', exist_ok=True)
    
    # Save results DataFrame
    results.to_csv('data/results/backtest_results.csv', index=False)
    print("Saved backtest results to data/results/backtest_results.csv")
    
    # Save detailed report
    report = strategy.generate_report(results)
    with open('data/results/backtest_report.txt', 'w') as f:
        f.write(report)
    print("Saved detailed report to data/results/backtest_report.txt")
    
    # Save portfolio returns if available
    try:
        portfolio_returns = strategy.calculate_portfolio_returns()
        portfolio_returns.to_csv('data/results/portfolio_returns.csv')
        print("Saved portfolio returns to data/results/portfolio_returns.csv")
    except Exception as e:
        print(f"Could not save portfolio returns: {e}")

def run_quick_test():
    """
    Run a quick test with a subset of stocks
    """
    print("Running quick test with 5 stocks...")
    
    # Use only first 5 stocks for quick testing
    test_symbols = cfg.NIFTY_50_SYMBOLS[:5]
    
    # First try with Dhan API
    stock_data = None
    try:
        from config.dhan_config import DHAN_CLIENT_CODE, DHAN_TOKEN_ID
        client_code = DHAN_CLIENT_CODE
        token_id = DHAN_TOKEN_ID
        
        data_loader = AsyncDataLoader(
            symbols=test_symbols,
            start_date='2023-01-01',
            end_date='2024-01-01',
            client_code=client_code,
            token_id=token_id,
            debug=False,
            max_workers=2
        )
        
        stock_data = data_loader.fetch_all_data_batch(batch_size=2)
        
    except ImportError:
        print("Dhan credentials not found for quick test")
    except Exception as e:
        print(f"Dhan API error: {e}")
    
    # If Dhan API failed or no subscription, use demo data
    if not stock_data:
        print("\n" + "=" * 60)
        print("SWITCHING TO DEMO MODE")
        print("=" * 60)
        print("Dhan API not available or no Data API subscription.")
        print("Running quick test with synthetic demo data...")
        print("Note: This is for testing the algorithm logic only.")
        print()
        
        try:
            from src.demo_data_generator import DemoDataGenerator
            
            demo_generator = DemoDataGenerator(
                symbols=test_symbols,
                start_date='2023-01-01',
                end_date='2024-01-01',
                debug=False
            )
            
            stock_data = demo_generator.generate_all_data()
            
        except Exception as e:
            print(f"Error generating demo data: {e}")
            return False
    
    # Run strategy if we have data
    if stock_data:
        strategy = MeanReversionStrategy()
        results = strategy.backtest_portfolio(stock_data)
        
        print("\nQuick Test Results:")
        print(f"Average strategy return: {results['strategy_return'].mean():.2%}")
        print(f"Average buy & hold return: {results['buyhold_return'].mean():.2%}")
        print(f"Average excess return: {results['excess_return'].mean():.2%}")
        
        # Show top performers
        print("\nTop 3 Performers:")
        top_performers = results.nlargest(3, 'strategy_return')
        for _, row in top_performers.iterrows():
            print(f"  {row['symbol']}: {row['strategy_return']:.2%} (vs {row['buyhold_return']:.2%} buy&hold)")
        
        return True
    else:
        print("Quick test failed - no data available")
        return False


def run_demo_algorithm():
    """
    Run the algorithm with demo/synthetic data
    """
    print("=" * 60)
    print("NIFTY 50 MEAN REVERSION ALGORITHM - DEMO MODE")
    print("=" * 60)
    print("Using synthetic data for demonstration purposes")
    print()
    
    # Step 1: Generate demo data
    print("Step 1: Generating synthetic stock data...")
    
    try:
        from src.demo_data_generator import DemoDataGenerator
        
        demo_generator = DemoDataGenerator(
            symbols=cfg.NIFTY_50_SYMBOLS,
            start_date=cfg.START_DATE,
            end_date=cfg.END_DATE,
            debug=False
        )
        
        stock_data = demo_generator.generate_all_data()
        
        if not stock_data:
            print("Failed to generate demo data. Exiting...")
            return False
        
        print(f"Successfully generated data for {len(stock_data)} stocks")
        print()
        
        # Step 2: Initialize strategy
        print("Step 2: Initializing mean reversion strategy...")
        strategy = MeanReversionStrategy(
            ma_period=cfg.MOVING_AVERAGE_PERIOD,
            short_percentile=cfg.SHORT_PERCENTILE,
            long_percentile=cfg.LONG_PERCENTILE
        )
        print(f"Strategy parameters:")
        print(f"  - Moving Average Period: {cfg.MOVING_AVERAGE_PERIOD}")
        print(f"  - Short Signal Percentile: {cfg.SHORT_PERCENTILE}")
        print(f"  - Long Signal Percentile: {cfg.LONG_PERCENTILE}")
        print()
        
        # Step 3: Run backtest
        print("Step 3: Running backtest on synthetic data...")
        results = strategy.backtest_portfolio(stock_data)
        print("Backtest completed!")
        print()
        
        # Step 4: Generate and display results
        print("Step 4: Analyzing results...")
        
        # Display summary statistics
        print("SUMMARY STATISTICS (DEMO DATA):")
        print(f"Number of stocks analyzed: {len(results)}")
        print(f"Average strategy return: {results['strategy_return'].mean():.2%}")
        print(f"Average buy & hold return: {results['buyhold_return'].mean():.2%}")
        print(f"Average excess return: {results['excess_return'].mean():.2%}")
        print()
        
        # Generate detailed report
        report = strategy.generate_report(results)
        print(report)
        
        # Step 5: Create simple tabular output
        print("Step 5: Creating tabular summary...")
        create_tabular_output(results)
        
        # Step 6: Save results with demo prefix
        print("Step 6: Saving demo results...")
        save_demo_results(results, strategy)
        
        print("=" * 60)
        print("DEMO ANALYSIS COMPLETE!")
        print("=" * 60)
        print("Note: Results are based on synthetic data for demonstration only.")
        print("For real trading, subscribe to Dhan Data APIs.")
        
        return True
        
    except Exception as e:
        print(f"Error in demo mode: {e}")
        return False


def save_demo_results(results, strategy):
    """
    Save demo results with appropriate naming
    """
    try:
        # Create demo results directory
        os.makedirs('data/demo_results', exist_ok=True)
        
        # Save results CSV
        results_file = 'data/demo_results/demo_backtest_results.csv'
        results.to_csv(results_file, index=False)
        print(f"Demo results saved to: {results_file}")
        
        # Save demo report
        report = strategy.generate_report(results)
        report_file = 'data/demo_results/demo_backtest_report.txt'
        with open(report_file, 'w') as f:
            f.write("DEMO MODE - SYNTHETIC DATA RESULTS\n")
            f.write("=" * 50 + "\n")
            f.write("Note: These results are based on synthetic data\n")
            f.write("and are for demonstration purposes only.\n\n")
            f.write(report)
        print(f"Demo report saved to: {report_file}")
        
    except Exception as e:
        print(f"Could not save demo results: {e}")


if __name__ == "__main__":
    # Check if we want to run a quick test first
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--quick-test':
        success = run_quick_test()
        if success:
            print("\nQuick test successful! Running full analysis...")
            main()
        else:
            print("Quick test failed. Please check your internet connection and try again.")
    else:
        main() 