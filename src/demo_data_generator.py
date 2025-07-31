#!/usr/bin/env python3
"""
Demo Data Generator for Mean Reversion Trading Algorithm
Generates synthetic stock data for testing when Dhan API is not available
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class DemoDataGenerator:
    """
    Generates synthetic stock data for testing purposes
    """
    
    def __init__(self, symbols, start_date='2023-01-01', end_date='2024-01-01', debug=False):
        """
        Initialize the demo data generator
        
        Args:
            symbols (list): List of stock symbols
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            debug (bool): Enable debug mode
        """
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.debug = debug
        
        # Set random seed for reproducible results
        np.random.seed(42)
        
    def generate_stock_data(self, symbol, initial_price=None):
        """
        Generate synthetic stock data for a single symbol using geometric Brownian motion
        
        Args:
            symbol (str): Stock symbol
            initial_price (float): Initial stock price (random if None)
            
        Returns:
            pd.DataFrame: Generated OHLCV data
        """
        if self.debug:
            print(f"Generating demo data for {symbol}...")
        
        # Create date range
        start_dt = pd.to_datetime(self.start_date)
        end_dt = pd.to_datetime(self.end_date)
        dates = pd.date_range(start=start_dt, end=end_dt, freq='D')
        
        # Remove weekends (assuming market is closed on weekends)
        dates = dates[dates.weekday < 5]
        
        num_days = len(dates)
        
        # Stock price parameters (realistic for Indian stocks)
        if initial_price is None:
            initial_price = np.random.uniform(100, 5000)  # Random initial price
        
        # Parameters for geometric Brownian motion
        mu = 0.0002  # Daily drift (about 5% annual return)
        sigma = 0.02  # Daily volatility (about 32% annual volatility)
        
        # Generate price path using geometric Brownian motion
        dt = 1  # Daily time step
        price_changes = np.random.normal(mu * dt, sigma * np.sqrt(dt), num_days)
        log_returns = np.cumsum(price_changes)
        prices = initial_price * np.exp(log_returns)
        
        # Generate OHLC data
        data = []
        
        for i, (date, close_price) in enumerate(zip(dates, prices)):
            # Generate intraday volatility
            intraday_vol = np.random.uniform(0.005, 0.025)  # 0.5% to 2.5% intraday range
            
            # Generate OHLC based on close price
            # Open price (with some gap from previous close)
            if i == 0:
                open_price = close_price * np.random.uniform(0.995, 1.005)
            else:
                # Open with gap from previous close
                open_price = data[i-1]['CLOSE'] * np.random.uniform(0.998, 1.002)
            
            # High and Low prices
            high_price = max(open_price, close_price) * np.random.uniform(1.0, 1.0 + intraday_vol)
            low_price = min(open_price, close_price) * np.random.uniform(1.0 - intraday_vol, 1.0)
            
            # Ensure OHLC logic is maintained
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            
            # Volume (realistic for liquid Indian stocks)
            base_volume = np.random.uniform(100000, 2000000)
            volume_multiplier = np.random.uniform(0.5, 2.0)  # Volume variation
            volume = int(base_volume * volume_multiplier)
            
            data.append({
                'DATE': date,
                'OPEN': round(open_price, 2),
                'HIGH': round(high_price, 2),
                'LOW': round(low_price, 2),
                'CLOSE': round(close_price, 2),
                'VOLUME': volume
            })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        df['DATE'] = pd.to_datetime(df['DATE'])
        df.set_index('DATE', inplace=True)
        
        # Add some mean reversion characteristics
        df = self._add_mean_reversion_patterns(df, symbol)
        
        if self.debug:
            print(f"✓ Generated {len(df)} days of data for {symbol}")
            print(f"  Price range: {df['LOW'].min():.2f} - {df['HIGH'].max():.2f}")
            print(f"  Volume range: {df['VOLUME'].min():,} - {df['VOLUME'].max():,}")
        
        return df
    
    def _add_mean_reversion_patterns(self, df, symbol):
        """
        Add some mean reversion patterns to make the data more realistic for testing
        
        Args:
            df (pd.DataFrame): Stock data
            symbol (str): Stock symbol
            
        Returns:
            pd.DataFrame: Modified data with mean reversion patterns
        """
        # Calculate moving average
        ma_period = 21
        df['MA'] = df['CLOSE'].rolling(window=ma_period).mean()
        
        # Add some mean reversion signals
        for i in range(ma_period, len(df)):
            ratio = df['CLOSE'].iloc[i] / df['MA'].iloc[i]
            
            # If price is too far from MA, add some reversion tendency
            if ratio > 1.1:  # Price 10% above MA
                # Add downward pressure
                reversion_factor = np.random.uniform(0.995, 0.999)
                df.loc[df.index[i], 'CLOSE'] *= reversion_factor
                df.loc[df.index[i], 'HIGH'] = max(df['HIGH'].iloc[i], df['CLOSE'].iloc[i])
                df.loc[df.index[i], 'LOW'] = min(df['LOW'].iloc[i], df['CLOSE'].iloc[i])
                
            elif ratio < 0.9:  # Price 10% below MA
                # Add upward pressure
                reversion_factor = np.random.uniform(1.001, 1.005)
                df.loc[df.index[i], 'CLOSE'] *= reversion_factor
                df.loc[df.index[i], 'HIGH'] = max(df['HIGH'].iloc[i], df['CLOSE'].iloc[i])
                df.loc[df.index[i], 'LOW'] = min(df['LOW'].iloc[i], df['CLOSE'].iloc[i])
        
        # Remove the MA column as it was just for pattern generation
        df.drop('MA', axis=1, inplace=True)
        
        return df
    
    def generate_all_data(self):
        """
        Generate synthetic data for all symbols
        
        Returns:
            dict: Dictionary with symbol as key and DataFrame as value
        """
        print("=" * 60)
        print("GENERATING DEMO DATA FOR TESTING")
        print("=" * 60)
        print(f"Generating synthetic data for {len(self.symbols)} symbols...")
        print(f"Date range: {self.start_date} to {self.end_date}")
        print("Note: This is synthetic data for testing purposes only")
        print()
        
        stock_data = {}
        
        # Base prices for some common Indian stocks (for realism)
        base_prices = {
            'RELIANCE': 2500, 'TCS': 3500, 'HDFCBANK': 1600, 'INFY': 1400, 'ICICIBANK': 950,
            'HINDUNILVR': 2600, 'ITC': 450, 'SBIN': 600, 'BHARTIARTL': 850, 'AXISBANK': 1100,
            'ADANIENT': 2800, 'ADANIPORTS': 750, 'APOLLOHOSP': 5200, 'ASIANPAINT': 3200
        }
        
        for symbol in self.symbols:
            initial_price = base_prices.get(symbol, np.random.uniform(500, 3000))
            
            try:
                data = self.generate_stock_data(symbol, initial_price)
                if data is not None and not data.empty:
                    stock_data[symbol] = data
                    print(f"✓ Generated data for {symbol}")
                else:
                    print(f"✗ Failed to generate data for {symbol}")
                    
            except Exception as e:
                print(f"✗ Error generating data for {symbol}: {e}")
        
        print(f"\nDemo data generation completed!")
        print(f"Successfully generated data for {len(stock_data)} out of {len(self.symbols)} symbols")
        
        return stock_data
    
    def save_demo_data(self, stock_data, directory='data/demo'):
        """
        Save generated demo data to CSV files
        
        Args:
            stock_data (dict): Generated stock data
            directory (str): Directory to save files
        """
        import os
        
        os.makedirs(directory, exist_ok=True)
        
        for symbol, data in stock_data.items():
            filename = os.path.join(directory, f"{symbol}_demo_data.csv")
            data.to_csv(filename)
            if self.debug:
                print(f"Saved demo data for {symbol} to {filename}")
        
        print(f"Demo data saved to {directory}/")

if __name__ == "__main__":
    # Quick test
    symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK']
    generator = DemoDataGenerator(symbols, debug=True)
    data = generator.generate_all_data()
    
    # Show sample
    if data:
        symbol = list(data.keys())[0]
        print(f"\nSample data for {symbol}:")
        print(data[symbol].head())
        print(f"\nData shape: {data[symbol].shape}")
