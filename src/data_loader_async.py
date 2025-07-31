#!/usr/bin/env python3
"""
Async Data Loader with Parallel Processing for Dhan API
This module provides parallel data fetching capabilities with proper rate limiting
"""

import pandas as pd
import numpy as np
import asyncio
import concurrent.futures
from datetime import datetime, timedelta
import warnings
import time
import random
warnings.filterwarnings('ignore')
from typing import Dict, List, Optional, Tuple

# Import Dhan API
try:
    from Dhan_Tradehull import Tradehull
except ImportError:
    print("Dhan-Tradehull not installed. Install with: pip install Dhan-Tradehull")
    Tradehull = None

class AsyncDataLoader:
    """
    Async data loader class for fetching Nifty 50 stock data using Dhan API with parallel processing
    """
    
    def __init__(self, symbols, start_date, end_date, client_code=None, token_id=None, debug=False, max_workers=10):
        """
        Initialize the async data loader
        
        Args:
            symbols (list): List of stock symbols
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            client_code (str): Dhan API client code
            token_id (str): Dhan API token ID
            debug (bool): Enable debug mode
            max_workers (int): Maximum number of parallel workers
        """
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.data = {}
        self.tsl = None
        self.debug = debug
        self.max_workers = max_workers
        
        # Rate limiting parameters
        try:
            from config.rate_limit_config import (
                RATE_LIMIT_DELAY, MAX_RETRIES, BACKOFF_FACTOR, MAX_WORKERS,
                BATCH_SIZE, BATCH_DELAY, CONTINUE_ON_RATE_LIMIT, LOG_RATE_LIMIT_ERRORS
            )
            self.rate_limit_delay = RATE_LIMIT_DELAY
            self.max_retries = MAX_RETRIES
            self.backoff_factor = BACKOFF_FACTOR
            self.max_workers = min(max_workers, MAX_WORKERS)  # Respect rate limit config
        except ImportError:
            # Fallback to default values
            self.rate_limit_delay = 3.0
            self.max_retries = 3
            self.backoff_factor = 2.0
            self.max_workers = min(max_workers, 3)  # Conservative default
        
        self.rate_limit_errors = 0  # Track rate limit errors
        self.last_request_time = 0  # Track last request time
        
        # Initialize Dhan connection if credentials provided
        if client_code and token_id:
            self._initialize_dhan_connection(client_code, token_id)
    
    def _initialize_dhan_connection(self, client_code, token_id):
        """
        Initialize connection to Dhan API
        """
        if Tradehull is None:
            print("Dhan-Tradehull not available")
            return False
            
        try:
            self.tsl = Tradehull(client_code, token_id)
            print("Successfully connected to Dhan API")
            return True
        except Exception as e:
            print(f"Failed to initialize Dhan connection: {e}")
            return False
    
    def _is_rate_limit_error(self, error_msg):
        """
        Check if the error is a rate limit error
        
        Args:
            error_msg (str): Error message
            
        Returns:
            bool: True if rate limit error
        """
        rate_limit_indicators = [
            'DH-904', 'Rate_Limit', 'Too many requests', 
            'rate limits', 'breaching rate limits'
        ]
        return any(indicator.lower() in str(error_msg).lower() for indicator in rate_limit_indicators)
    
    def _is_subscription_error(self, error_msg):
        """
        Check if the error is a subscription/access error
        
        Args:
            error_msg (str): Error message
            
        Returns:
            bool: True if subscription error
        """
        subscription_indicators = [
            'DH-902', 'Invalid_Access', 'not subscribed to Data APIs',
            'does not have access to Trading APIs', 'HTTP Status 451'
        ]
        return any(indicator in str(error_msg) for indicator in subscription_indicators)
    
    def _handle_rate_limit(self, attempt):
        """
        Handle rate limiting with exponential backoff
        
        Args:
            attempt (int): Current attempt number
        """
        if attempt == 1:
            # First rate limit error - wait longer
            delay = self.rate_limit_delay * self.backoff_factor
        else:
            # Subsequent errors - exponential backoff
            delay = self.rate_limit_delay * (self.backoff_factor ** attempt)
        
        # Add some randomness to avoid thundering herd
        delay += random.uniform(0.5, 2.0)
        
        print(f"⚠️  Rate limit detected. Waiting {delay:.1f} seconds before retry {attempt}...")
        time.sleep(delay)
        self.rate_limit_errors += 1
    
    def _respect_rate_limits(self):
        """
        Ensure minimum delay between requests
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def fetch_stock_data_sync(self, symbol, exchange='NSE', timeframe='DAY'):
        """
        Synchronous method to fetch data for a single stock with rate limiting
        """
        if not self.tsl:
            print(f"No Dhan connection available for {symbol}")
            return None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                # Respect rate limits
                self._respect_rate_limits()
                
                # Get historical data from Dhan API
                data = self.tsl.get_historical_data(
                    tradingsymbol=symbol,
                    exchange=exchange,
                    timeframe=timeframe,
                    debug="NO"
                )
                
                # Debug: Print data type and structure
                if self.debug:
                    print(f"Data type for {symbol}: {type(data)}")
                    if isinstance(data, (dict, list)):
                        print(f"Data length: {len(data)}")
                    elif isinstance(data, pd.DataFrame):
                        print(f"DataFrame shape: {data.shape}")
                
                # Handle different data types returned by Dhan API
                if data is not None:
                    # If data is already a DataFrame
                    if isinstance(data, pd.DataFrame):
                        df = data
                    # If data is a dict, convert to DataFrame
                    elif isinstance(data, dict):
                        df = pd.DataFrame(data)
                    # If data is a list, convert to DataFrame
                    elif isinstance(data, list):
                        df = pd.DataFrame(data)
                    else:
                        print(f"Unexpected data type for {symbol}: {type(data)}")
                        return None
                    
                    # Check if DataFrame is not empty
                    if not df.empty:
                        # Standardize column names - handle both lowercase and uppercase
                        column_mapping = {
                            'open': 'OPEN',
                            'high': 'HIGH', 
                            'low': 'LOW',
                            'close': 'CLOSE',
                            'volume': 'VOLUME',
                            'timestamp': 'DATE',
                            'time': 'DATE',
                            'datetime': 'DATE'
                        }
                        
                        # Rename columns to standard format
                        df.columns = [column_mapping.get(col.lower(), col.upper()) for col in df.columns]
                        
                        # Ensure required columns exist
                        required_cols = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']
                        missing_cols = []
                        for col in required_cols:
                            if col not in df.columns:
                                missing_cols.append(col)
                        
                        if missing_cols:
                            print(f"Missing columns for {symbol}: {missing_cols}")
                            print(f"Available columns: {list(df.columns)}")
                            print(f"Column mapping issue - trying to fix...")
                            
                            # Try to fix common column name issues
                            if 'TIMESTAMP' in df.columns and 'DATE' not in df.columns:
                                df = df.rename(columns={'TIMESTAMP': 'DATE'})
                                print(f"Renamed TIMESTAMP to DATE for {symbol}")
                            
                            # Recheck after potential fixes
                            missing_cols = []
                            for col in required_cols:
                                if col not in df.columns:
                                    missing_cols.append(col)
                            
                            if missing_cols:
                                print(f"Still missing columns for {symbol}: {missing_cols}")
                                return None
                        
                        # Convert date column
                        if 'DATE' in df.columns:
                            df['DATE'] = pd.to_datetime(df['DATE'])
                            df.set_index('DATE', inplace=True)
                            if self.debug:
                                print(f"✓ Date column processed for {symbol}")
                        else:
                            print(f"❌ No DATE column found for {symbol}")
                            return None
                        
                        # Convert numeric columns
                        numeric_cols = ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']
                        for col in numeric_cols:
                            if col in df.columns:
                                df[col] = pd.to_numeric(df[col], errors='coerce')
                                if self.debug:
                                    print(f"✓ Converted {col} to numeric for {symbol}")
                        
                        # Filter by date range
                        if self.start_date and self.end_date:
                            start_dt = pd.to_datetime(self.start_date)
                            end_dt = pd.to_datetime(self.end_date)
                            df = df[(df.index >= start_dt) & (df.index <= end_dt)]
                            if self.debug:
                                print(f"✓ Filtered data for date range for {symbol}")
                        
                        if self.debug:
                            print(f"✓ Successfully processed data for {symbol}: {df.shape}")
                        
                        return df
                    else:
                        print(f"Empty DataFrame received for {symbol}")
                        return None
                else:
                    print(f"No data received for {symbol}")
                    return None
                    
            except Exception as e:
                error_msg = str(e)
                print(f"Exception in Getting OHLC data as {error_msg}")
                
                # Check if it's a subscription error first
                if self._is_subscription_error(error_msg):
                    print(f"❌ Subscription Error for {symbol}:")
                    print("   Your Dhan account does not have access to Data APIs.")
                    print("   Please subscribe to Dhan Data APIs to fetch real market data.")
                    print("   For testing, you can use demo mode (--demo flag).")
                    return None
                
                # Check if it's a rate limit error
                elif self._is_rate_limit_error(error_msg):
                    if attempt < self.max_retries:
                        self._handle_rate_limit(attempt)
                        continue
                    else:
                        print(f"✗ Failed to fetch data for {symbol} after {self.max_retries} attempts due to rate limiting")
                        return None
                else:
                    # Non-rate limit error
                    print(f"✗ Failed to fetch data for {symbol}: {error_msg}")
                    return None
        
        return None
    
    def fetch_all_data_parallel(self):
        """
        Fetch data for all symbols using parallel processing with rate limiting
        
        Returns:
            dict: Dictionary with symbol as key and data as value
        """
        if not self.tsl:
            print("Dhan connection not available. Please provide client_code and token_id.")
            return {}
        
        print(f"Fetching Nifty 50 stock data using Dhan API with {self.max_workers} parallel workers...")
        print(f"Rate limiting: {self.rate_limit_delay}s delay between requests, {self.max_retries} retries")
        start_time = time.time()
        
        successful_fetches = 0
        failed_fetches = 0
        
        # Use fewer workers to avoid overwhelming the API
        workers = min(5, self.max_workers)  # Limit to 5 workers max
        print(f"Using {workers} workers to respect rate limits")
        
        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit all tasks
            future_to_symbol = {
                executor.submit(self.fetch_stock_data_sync, symbol): symbol 
                for symbol in self.symbols
            }
            
            # Process completed tasks
            for future in concurrent.futures.as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data = future.result()
                    if data is not None and not data.empty:
                        self.data[symbol] = data
                        successful_fetches += 1
                        print(f"✓ Successfully fetched data for {symbol}")
                    else:
                        failed_fetches += 1
                        print(f"✗ Failed to fetch data for {symbol}")
                except Exception as e:
                    failed_fetches += 1
                    print(f"✗ Error fetching {symbol}: {str(e)}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\nFetch Summary:")
        print(f"  Successful: {successful_fetches}")
        print(f"  Failed: {failed_fetches}")
        print(f"  Total: {len(self.symbols)}")
        print(f"  Rate limit errors: {self.rate_limit_errors}")
        print(f"  Time taken: {total_time:.2f} seconds")
        print(f"  Average time per symbol: {total_time/len(self.symbols):.2f} seconds")
        
        if successful_fetches == 0:
            print("⚠️  No data fetched successfully. Please check:")
            print("  1. Dhan API credentials")
            print("  2. Internet connection")
            print("  3. Market hours (9:15 AM - 3:30 PM IST)")
            print("  4. Symbol names are correct")
            print("  5. Rate limiting - try using batch processing instead")
        
        return self.data
    
    def fetch_all_data_batch(self, batch_size=5):
        """
        Fetch data in batches to avoid overwhelming the API with improved rate limiting
        
        Args:
            batch_size (int): Number of symbols to process in each batch
        """
        if not self.tsl:
            print("Dhan connection not available. Please provide client_code and token_id.")
            return {}
        
        print(f"Fetching Nifty 50 stock data in batches of {batch_size}...")
        print(f"Rate limiting: {self.rate_limit_delay}s delay between requests, {self.max_retries} retries")
        start_time = time.time()
        
        successful_fetches = 0
        failed_fetches = 0
        
        # Process symbols in batches
        for i in range(0, len(self.symbols), batch_size):
            batch_symbols = self.symbols[i:i + batch_size]
            print(f"\nProcessing batch {i//batch_size + 1}: {batch_symbols}")
            
            # Use fewer workers for batch processing to reduce API load
            workers = min(2, batch_size, self.max_workers)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_symbol = {
                    executor.submit(self.fetch_stock_data_sync, symbol): symbol 
                    for symbol in batch_symbols
                }
                
                for future in concurrent.futures.as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    try:
                        data = future.result()
                        if data is not None and not data.empty:
                            self.data[symbol] = data
                            successful_fetches += 1
                            print(f"✓ Successfully fetched data for {symbol}")
                        else:
                            failed_fetches += 1
                            print(f"✗ Failed to fetch data for {symbol}")
                    except Exception as e:
                        failed_fetches += 1
                        print(f"✗ Error fetching {symbol}: {str(e)}")
            
            # Longer delay between batches to be more respectful to the API
            if i + batch_size < len(self.symbols):
                delay = max(3.0, self.rate_limit_delay * 2)  # At least 3 seconds between batches
                print(f"Waiting {delay:.1f}s before next batch...")
                time.sleep(delay)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\nFetch Summary:")
        print(f"  Successful: {successful_fetches}")
        print(f"  Failed: {failed_fetches}")
        print(f"  Total: {len(self.symbols)}")
        print(f"  Rate limit errors: {self.rate_limit_errors}")
        print(f"  Time taken: {total_time:.2f} seconds")
        print(f"  Average time per symbol: {total_time/len(self.symbols):.2f} seconds")
        
        return self.data
    
    def get_closing_prices(self):
        """
        Get closing prices for all stocks
        
        Returns:
            pd.DataFrame: DataFrame with dates as index and symbols as columns
        """
        if not self.data:
            print("No data available. Run fetch_all_data_parallel() first.")
            return pd.DataFrame()
            
        closing_prices = pd.DataFrame()
        
        for symbol, data in self.data.items():
            if 'CLOSE' in data.columns:
                closing_prices[symbol] = data['CLOSE']
            
        return closing_prices
    
    def get_returns(self):
        """
        Calculate log returns for all stocks
        
        Returns:
            pd.DataFrame: DataFrame with log returns
        """
        closing_prices = self.get_closing_prices()
        if closing_prices.empty:
            return pd.DataFrame()
            
        # Calculate returns using pandas methods
        returns = closing_prices.pct_change()  # Using percentage change instead of log returns
        return returns
    
    def get_ltp_data(self, symbols=None):
        """
        Get live LTP data for symbols
        
        Args:
            symbols (list): List of symbols (uses self.symbols if None)
            
        Returns:
            dict: Symbol to LTP mapping
        """
        if not self.tsl:
            print("Dhan connection not available")
            return {}
        
        if symbols is None:
            symbols = self.symbols
            
        try:
            data = self.tsl.get_ltp_data(
                names=symbols,
                debug="NO"
            )
            
            if isinstance(data, dict):
                # Extract LTP values
                ltp_data = {}
                for symbol, symbol_data in data.items():
                    if isinstance(symbol_data, dict) and 'ltp' in symbol_data:
                        ltp_data[symbol] = float(symbol_data['ltp'])
                    elif isinstance(symbol_data, (int, float)):
                        ltp_data[symbol] = float(symbol_data)
                
                return ltp_data
            else:
                print(f"Invalid LTP data format: {data}")
                return {}
                
        except Exception as e:
            print(f"Error fetching LTP data: {e}")
            return {}
    
    def save_data_to_csv(self, filename='nifty50_data.csv'):
        """
        Save all stock data to CSV files
        
        Args:
            filename (str): Base filename for saving data
        """
        if not self.data:
            print("No data available. Run fetch_all_data_parallel() first.")
            return
            
        for symbol, data in self.data.items():
            safe_symbol = symbol.replace('.', '_')
            data.to_csv(f"{safe_symbol}_{filename}")
            print(f"Saved {symbol} data to {safe_symbol}_{filename}")
    
    def get_data_summary(self):
        """
        Get summary statistics for all stocks
        
        Returns:
            pd.DataFrame: Summary statistics
        """
        if not self.data:
            print("No data available. Run fetch_all_data_parallel() first.")
            return pd.DataFrame()
            
        summary_data = []
        
        for symbol, data in self.data.items():
            if 'CLOSE' in data.columns:
                summary = {
                    'Symbol': symbol,
                    'Start_Date': data.index[0].strftime('%Y-%m-%d'),
                    'End_Date': data.index[-1].strftime('%Y-%m-%d'),
                    'Total_Days': len(data),
                    'Initial_Price': data['CLOSE'].iloc[0],
                    'Final_Price': data['CLOSE'].iloc[-1],
                    'Total_Return': (data['CLOSE'].iloc[-1] / data['CLOSE'].iloc[0] - 1) * 100,
                    'Volatility': data['CLOSE'].pct_change().std() * np.sqrt(252) * 100,
                    'Max_Price': data['HIGH'].max() if 'HIGH' in data.columns else data['CLOSE'].max(),
                    'Min_Price': data['LOW'].min() if 'LOW' in data.columns else data['CLOSE'].min(),
                    'Avg_Volume': data['VOLUME'].mean() if 'VOLUME' in data.columns else 0
                }
                summary_data.append(summary)
            
        return pd.DataFrame(summary_data) 