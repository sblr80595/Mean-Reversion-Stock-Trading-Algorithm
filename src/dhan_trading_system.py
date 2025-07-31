#!/usr/bin/env python3
"""
Dhan API Integration for Mean Reversion Trading Algorithm
This module provides live trading capabilities using Dhan API
"""

import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Import Dhan API
try:
    from Dhan_Tradehull import Tradehull
except ImportError:
    print("Dhan-Tradehull not installed. Install with: pip install Dhan-Tradehull")
    Tradehull = None

from config import *
from mean_reversion_strategy import MeanReversionStrategy

class DhanTradingSystem:
    """
    Live trading system using Dhan API with mean reversion strategy
    """
    
    def __init__(self, client_code: str, token_id: str, debug: bool = False):
        """
        Initialize the Dhan trading system
        
        Args:
            client_code (str): Dhan API client code
            token_id (str): Dhan API token ID
            debug (bool): Enable debug mode
        """
        self.client_code = client_code
        self.token_id = token_id
        self.debug = debug
        self.tsl = None
        self.strategy = MeanReversionStrategy(
            ma_period=MOVING_AVERAGE_PERIOD,
            short_percentile=SHORT_PERCENTILE,
            long_percentile=LONG_PERCENTILE
        )
        self.positions = {}
        self.orders = {}
        self.portfolio_value = 0
        self.risk_management = {
            'max_position_size': MAX_POSITION_SIZE,
            'stop_loss_pct': STOP_LOSS_PERCENTAGE,
            'take_profit_pct': TAKE_PROFIT_PERCENTAGE
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trading_log.txt'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize Dhan connection
        self._initialize_dhan_connection()
    
    def _initialize_dhan_connection(self):
        """
        Initialize connection to Dhan API
        """
        if Tradehull is None:
            self.logger.error("Dhan-Tradehull not available")
            return False
            
        try:
            self.tsl = Tradehull(self.client_code, self.token_id)
            self.logger.info("Successfully connected to Dhan API")
            
            # Test connection by getting balance
            balance = self.get_balance()
            if balance:
                self.logger.info(f"Account balance: ₹{balance}")
                return True
            else:
                self.logger.error("Failed to get account balance")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Dhan connection: {e}")
            return False
    
    def get_balance(self) -> Optional[float]:
        """
        Get account balance
        
        Returns:
            float: Available balance
        """
        if not self.tsl:
            return None
            
        try:
            balance_data = self.tsl.get_balance()
            if isinstance(balance_data, dict) and 'status' in balance_data:
                if balance_data['status'] == 'success':
                    return float(balance_data.get('data', {}).get('availableBalance', 0))
                else:
                    self.logger.error(f"Balance fetch failed: {balance_data}")
                    return None
            return balance_data
        except Exception as e:
            self.logger.error(f"Error getting balance: {e}")
            return None
    
    def get_live_pnl(self) -> Optional[float]:
        """
        Get live P&L
        
        Returns:
            float: Current P&L
        """
        if not self.tsl:
            return None
            
        try:
            pnl_data = self.tsl.get_live_pnl()
            if isinstance(pnl_data, dict) and 'status' in pnl_data:
                if pnl_data['status'] == 'success':
                    return float(pnl_data.get('data', {}).get('totalPnl', 0))
                else:
                    self.logger.error(f"P&L fetch failed: {pnl_data}")
                    return None
            return pnl_data
        except Exception as e:
            self.logger.error(f"Error getting P&L: {e}")
            return None
    
    def get_historical_data(self, symbol: str, exchange: str = 'NSE', 
                          timeframe: str = 'DAY', days: int = 100) -> Optional[pd.DataFrame]:
        """
        Get historical data for a symbol
        
        Args:
            symbol (str): Trading symbol
            exchange (str): Exchange (NSE, INDEX, etc.)
            timeframe (str): Timeframe (1, 5, 15, 60, DAY)
            days (int): Number of days to fetch
            
        Returns:
            pd.DataFrame: Historical data
        """
        if not self.tsl:
            return None
            
        try:
            # Get historical data
            data = self.tsl.get_historical_data(
                tradingsymbol=symbol,
                exchange=exchange,
                timeframe=timeframe,
                debug="YES" if self.debug else "NO"
            )
            
            if data and isinstance(data, dict):
                # Convert to DataFrame
                df = pd.DataFrame(data)
                if not df.empty:
                    # Standardize column names
                    df.columns = [col.upper() for col in df.columns]
                    
                    # Ensure required columns exist
                    required_cols = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']
                    for col in required_cols:
                        if col not in df.columns:
                            # Try alternative column names
                            alt_names = {
                                'DATE': ['TIMESTAMP', 'TIME', 'DATETIME'],
                                'OPEN': ['O'],
                                'HIGH': ['H'],
                                'LOW': ['L'],
                                'CLOSE': ['C'],
                                'VOLUME': ['VOL', 'QUANTITY']
                            }
                            if col in alt_names:
                                for alt in alt_names[col]:
                                    if alt in df.columns:
                                        df[col] = df[alt]
                                        break
                    
                    # Convert date column
                    if 'DATE' in df.columns:
                        df['DATE'] = pd.to_datetime(df['DATE'])
                        df.set_index('DATE', inplace=True)
                    
                    # Convert numeric columns
                    numeric_cols = ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']
                    for col in numeric_cols:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    return df
                    
            self.logger.error(f"No valid data received for {symbol}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    def get_ltp_data(self, symbols: List[str]) -> Dict[str, float]:
        """
        Get live LTP data for symbols
        
        Args:
            symbols (List[str]): List of symbols
            
        Returns:
            Dict[str, float]: Symbol to LTP mapping
        """
        if not self.tsl:
            return {}
            
        try:
            data = self.tsl.get_ltp_data(
                names=symbols,
                debug="YES" if self.debug else "NO"
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
                self.logger.error(f"Invalid LTP data format: {data}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error fetching LTP data: {e}")
            return {}
    
    def calculate_signals_for_symbol(self, symbol: str, exchange: str = 'NSE') -> Dict:
        """
        Calculate trading signals for a symbol
        
        Args:
            symbol (str): Trading symbol
            exchange (str): Exchange
            
        Returns:
            Dict: Signal information
        """
        # Get historical data
        historical_data = self.get_historical_data(symbol, exchange)
        
        if historical_data is None or historical_data.empty:
            self.logger.warning(f"No historical data available for {symbol}")
            return {
                'symbol': symbol,
                'signal': 'HOLD',
                'reason': 'No historical data',
                'current_price': None,
                'ma_value': None,
                'ratio': None
            }
        
        # Calculate signals using strategy
        result_data = self.strategy.calculate_signals(historical_data.copy())
        
        # Get current position
        current_position = result_data['position'].iloc[-1] if not result_data['position'].isna().all() else 0
        
        # Get current values
        current_price = result_data['Close'].iloc[-1]
        ma_value = result_data['ma'].iloc[-1]
        ratio = result_data['ratio'].iloc[-1]
        
        # Determine signal
        if pd.isna(current_position):
            signal = 'HOLD'
            reason = 'No clear signal'
        elif current_position == 1:
            signal = 'BUY'
            reason = f'Ratio {ratio:.3f} below {self.strategy.long_percentile}th percentile'
        elif current_position == -1:
            signal = 'SELL'
            reason = f'Ratio {ratio:.3f} above {self.strategy.short_percentile}th percentile'
        else:
            signal = 'HOLD'
            reason = 'Position maintained'
        
        return {
            'symbol': symbol,
            'signal': signal,
            'reason': reason,
            'current_price': current_price,
            'ma_value': ma_value,
            'ratio': ratio,
            'position': current_position
        }
    
    def place_order(self, symbol: str, transaction_type: str, quantity: int, 
                   price: float = 0, order_type: str = 'MARKET') -> bool:
        """
        Place an order
        
        Args:
            symbol (str): Trading symbol
            transaction_type (str): BUY or SELL
            quantity (int): Quantity
            price (float): Price (0 for market orders)
            order_type (str): MARKET or LIMIT
            
        Returns:
            bool: Success status
        """
        if not self.tsl:
            self.logger.error("Dhan connection not available")
            return False
        
        try:
            # Place order using Dhan API
            order_result = self.tsl.place_order(
                tradingsymbol=symbol,
                exchange='NSE',
                transaction_type=transaction_type,
                quantity=quantity,
                price=price,
                order_type=order_type,
                debug="YES" if self.debug else "NO"
            )
            
            if isinstance(order_result, dict) and order_result.get('status') == 'success':
                order_id = order_result.get('data', {}).get('orderId')
                self.logger.info(f"Order placed successfully: {transaction_type} {quantity} {symbol} at {price}")
                self.orders[order_id] = {
                    'symbol': symbol,
                    'type': transaction_type,
                    'quantity': quantity,
                    'price': price,
                    'status': 'PENDING'
                }
                return True
            else:
                self.logger.error(f"Order placement failed: {order_result}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return False
    
    def get_positions(self) -> Dict:
        """
        Get current positions
        
        Returns:
            Dict: Current positions
        """
        if not self.tsl:
            return {}
        
        try:
            positions_data = self.tsl.get_positions()
            if isinstance(positions_data, dict) and positions_data.get('status') == 'success':
                return positions_data.get('data', {})
            else:
                self.logger.error(f"Failed to get positions: {positions_data}")
                return {}
        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
            return {}
    
    def run_live_trading(self, symbols: List[str], check_interval: int = 300):
        """
        Run live trading system
        
        Args:
            symbols (List[str]): List of symbols to trade
            check_interval (int): Check interval in seconds
        """
        self.logger.info(f"Starting live trading for {len(symbols)} symbols")
        self.logger.info(f"Check interval: {check_interval} seconds")
        
        while True:
            try:
                self.logger.info("=" * 50)
                self.logger.info(f"Trading cycle at {datetime.now()}")
                
                # Get account balance
                balance = self.get_balance()
                if balance:
                    self.logger.info(f"Available balance: ₹{balance}")
                
                # Get current P&L
                pnl = self.get_live_pnl()
                if pnl is not None:
                    self.logger.info(f"Current P&L: ₹{pnl}")
                
                # Analyze each symbol
                for symbol in symbols:
                    self.logger.info(f"Analyzing {symbol}...")
                    
                    # Calculate signals
                    signal_data = self.calculate_signals_for_symbol(symbol)
                    
                    if signal_data['signal'] != 'HOLD':
                        self.logger.info(f"Signal for {symbol}: {signal_data['signal']} - {signal_data['reason']}")
                        
                        # Check if we should place an order
                        if self._should_place_order(symbol, signal_data):
                            # Calculate position size
                            position_size = self._calculate_position_size(balance, signal_data['current_price'])
                            
                            if position_size > 0:
                                # Place order
                                success = self.place_order(
                                    symbol=symbol,
                                    transaction_type=signal_data['signal'],
                                    quantity=position_size,
                                    price=0,  # Market order
                                    order_type='MARKET'
                                )
                                
                                if success:
                                    self.logger.info(f"Order placed for {symbol}")
                                else:
                                    self.logger.error(f"Failed to place order for {symbol}")
                    else:
                        self.logger.info(f"No signal for {symbol}")
                
                # Wait for next cycle
                self.logger.info(f"Waiting {check_interval} seconds for next cycle...")
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                self.logger.info("Trading stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in trading cycle: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _should_place_order(self, symbol: str, signal_data: Dict) -> bool:
        """
        Determine if an order should be placed
        
        Args:
            symbol (str): Trading symbol
            signal_data (Dict): Signal data
            
        Returns:
            bool: Should place order
        """
        # Check if we already have a position
        current_positions = self.get_positions()
        
        if symbol in current_positions:
            current_position = current_positions[symbol]
            
            # If we have a long position and signal is SELL
            if current_position > 0 and signal_data['signal'] == 'SELL':
                return True
            
            # If we have a short position and signal is BUY
            elif current_position < 0 and signal_data['signal'] == 'BUY':
                return True
            
            # If we have no position and signal is BUY or SELL
            elif current_position == 0 and signal_data['signal'] in ['BUY', 'SELL']:
                return True
        else:
            # No current position, place order if signal is BUY or SELL
            return signal_data['signal'] in ['BUY', 'SELL']
        
        return False
    
    def _calculate_position_size(self, balance: float, current_price: float) -> int:
        """
        Calculate position size based on risk management
        
        Args:
            balance (float): Available balance
            current_price (float): Current price
            
        Returns:
            int: Position size in quantity
        """
        if not balance or not current_price:
            return 0
        
        # Calculate maximum position value
        max_position_value = balance * self.risk_management['max_position_size']
        
        # Calculate quantity
        quantity = int(max_position_value / current_price)
        
        # Ensure minimum quantity
        if quantity < 1:
            return 0
        
        return quantity
    
    def get_portfolio_summary(self) -> Dict:
        """
        Get portfolio summary
        
        Returns:
            Dict: Portfolio summary
        """
        summary = {
            'balance': self.get_balance(),
            'pnl': self.get_live_pnl(),
            'positions': self.get_positions(),
            'orders': self.orders
        }
        
        return summary

def main():
    """
    Main function for Dhan trading system
    """
    print("=" * 60)
    print("DHAN API MEAN REVERSION TRADING SYSTEM")
    print("=" * 60)
    
    # Configuration
    CLIENT_CODE = "your_client_code"  # Replace with your Dhan client code
    TOKEN_ID = "your_token_id"        # Replace with your Dhan token ID
    
    # Trading symbols (Nifty 50 stocks)
    TRADING_SYMBOLS = [
        'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
        'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'AXISBANK'
    ]
    
    # Initialize trading system
    trading_system = DhanTradingSystem(
        client_code=CLIENT_CODE,
        token_id=TOKEN_ID,
        debug=True
    )
    
    # Check connection
    if not trading_system.tsl:
        print("Failed to connect to Dhan API. Please check your credentials.")
        return
    
    print("Successfully connected to Dhan API!")
    
    # Get initial portfolio summary
    portfolio = trading_system.get_portfolio_summary()
    print(f"Initial balance: ₹{portfolio['balance']}")
    print(f"Current P&L: ₹{portfolio['pnl']}")
    
    # Run live trading
    try:
        trading_system.run_live_trading(
            symbols=TRADING_SYMBOLS,
            check_interval=300  # Check every 5 minutes
        )
    except KeyboardInterrupt:
        print("\nTrading stopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 