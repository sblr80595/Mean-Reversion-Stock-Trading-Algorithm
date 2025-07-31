import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import Dhan API
try:
    from Dhan_Tradehull import Tradehull
except ImportError:
    print("Dhan-Tradehull not installed. Install with: pip install Dhan-Tradehull")
    Tradehull = None

class DataLoader:
    """
    Data loader class for fetching Nifty 50 stock data using Dhan API
    """
    
    def __init__(self, symbols, start_date, end_date, client_code=None, token_id=None, debug=False):
        """
        Initialize the data loader
        
        Args:
            symbols (list): List of stock symbols
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            client_code (str): Dhan API client code
            token_id (str): Dhan API token ID
            debug (bool): Enable debug mode
        """
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.data = {}
        self.tsl = None
        self.debug = debug
        
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
    
    def fetch_stock_data(self, symbol, exchange='NSE', timeframe='DAY'):
        """
        Fetch data for a single stock using Dhan API
        
        Args:
            symbol (str): Stock symbol
            exchange (str): Exchange (NSE, INDEX, etc.)
            timeframe (str): Timeframe (1, 5, 15, 60, DAY)
            
        Returns:
            pd.DataFrame: Stock data with OHLCV
        """
        if not self.tsl:
            print(f"No Dhan connection available for {symbol}")
            return None
            
        try:
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
                print(f"Data sample: {data}")
            
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
                        return None
                    
                    # Convert date column
                    if 'DATE' in df.columns:
                        df['DATE'] = pd.to_datetime(df['DATE'])
                        df.set_index('DATE', inplace=True)
                    
                    # Convert numeric columns
                    numeric_cols = ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']
                    for col in numeric_cols:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # Filter by date range
                    if self.start_date and self.end_date:
                        start_dt = pd.to_datetime(self.start_date)
                        end_dt = pd.to_datetime(self.end_date)
                        df = df[(df.index >= start_dt) & (df.index <= end_dt)]
                    
                    return df
                else:
                    print(f"Empty DataFrame received for {symbol}")
                    return None
            else:
                print(f"No data received for {symbol}")
                return None
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def fetch_all_data(self):
        """
        Fetch data for all symbols using Dhan API
        
        Returns:
            dict: Dictionary with symbol as key and data as value
        """
        if not self.tsl:
            print("Dhan connection not available. Please provide client_code and token_id.")
            return {}
        
        print("Fetching Nifty 50 stock data using Dhan API...")
        
        successful_fetches = 0
        failed_fetches = 0
        
        for symbol in self.symbols:
            try:
                print(f"Fetching data for {symbol}...")
                data = self.fetch_stock_data(symbol)
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
                continue
                
        print(f"\nFetch Summary:")
        print(f"  Successful: {successful_fetches}")
        print(f"  Failed: {failed_fetches}")
        print(f"  Total: {len(self.symbols)}")
        
        if successful_fetches == 0:
            print("⚠️  No data fetched successfully. Please check:")
            print("  1. Dhan API credentials")
            print("  2. Internet connection")
            print("  3. Market hours (9:15 AM - 3:30 PM IST)")
            print("  4. Symbol names are correct")
        
        return self.data
    
    def get_closing_prices(self):
        """
        Get closing prices for all stocks
        
        Returns:
            pd.DataFrame: DataFrame with dates as index and symbols as columns
        """
        if not self.data:
            print("No data available. Run fetch_all_data() first.")
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
            
        returns = np.log(closing_prices).diff()
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
            print("No data available. Run fetch_all_data() first.")
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
            print("No data available. Run fetch_all_data() first.")
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