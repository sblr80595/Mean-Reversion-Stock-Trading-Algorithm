#!/usr/bin/env python3
"""
Live Data Only Trading System for Dhan API
Works with basic API access (no historical data required)
"""

import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
from concurrent.futures import ThreadPoolExecutor
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/live_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LiveDataCollector:
    """Collects live market data using available Dhan APIs"""
    
    def __init__(self, client_code: str, token_id: str):
        self.client_code = client_code
        self.token_id = token_id
        self.tsl = None
        self.data_buffer = {}  # Store recent data points
        self.is_running = False
        self.lock = threading.Lock()
        
        # Initialize connection
        self._connect()
    
    def _connect(self):
        """Initialize Dhan connection"""
        try:
            from Dhan_Tradehull import Tradehull
            self.tsl = Tradehull(self.client_code, self.token_id)
            logger.info("✓ Connected to Dhan API")
        except Exception as e:
            logger.error(f"Failed to connect to Dhan API: {e}")
            raise
    
    def get_account_info(self) -> Dict:
        """Get account balance and basic info"""
        try:
            balance = self.tsl.get_balance()
            holdings = self.tsl.get_holdings()
            
            return {
                'balance': balance,
                'holdings': holdings,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return {}
    
    def get_available_methods(self) -> List[str]:
        """Get list of available API methods"""
        methods = []
        for method in dir(self.tsl):
            if not method.startswith('_') and callable(getattr(self.tsl, method)):
                methods.append(method)
        return methods
    
    def collect_live_data(self, symbols: List[str]) -> Dict:
        """
        Collect whatever live data is available
        This is a fallback method since historical data isn't available
        """
        live_data = {}
        
        for symbol in symbols:
            try:
                # Try different methods to get data
                data = self._get_symbol_data(symbol)
                if data:
                    live_data[symbol] = data
                    
            except Exception as e:
                logger.warning(f"Could not get data for {symbol}: {e}")
        
        return live_data
    
    def _get_symbol_data(self, symbol: str) -> Optional[Dict]:
        """Try to get data for a symbol using available methods"""
        try:
            # Method 1: Try get_historical_data (might work for recent data)
            data = self.tsl.get_historical_data(
                tradingsymbol=symbol,
                exchange='NSE',
                timeframe='DAY',
                debug="NO"
            )
            
            if data is not None and not isinstance(data, dict):
                # Convert to DataFrame if it's data
                if hasattr(data, 'shape'):
                    return {
                        'type': 'historical',
                        'data': data,
                        'timestamp': datetime.now().isoformat()
                    }
            
        except Exception as e:
            logger.debug(f"Historical data failed for {symbol}: {e}")
        
        # Method 2: Try to get any available data
        try:
            # Check if there are other methods available
            methods = self.get_available_methods()
            logger.info(f"Available methods: {methods}")
            
            # Try common method names
            for method_name in ['get_ltp', 'get_market_data', 'get_quote']:
                if hasattr(self.tsl, method_name):
                    method = getattr(self.tsl, method_name)
                    try:
                        result = method(symbol, 'NSE')
                        if result:
                            return {
                                'type': 'live',
                                'method': method_name,
                                'data': result,
                                'timestamp': datetime.now().isoformat()
                            }
                    except Exception as e:
                        logger.debug(f"Method {method_name} failed: {e}")
                        
        except Exception as e:
            logger.debug(f"Alternative methods failed for {symbol}: {e}")
        
        return None

class LiveMeanReversionStrategy:
    """Mean Reversion Strategy adapted for live data"""
    
    def __init__(self, lookback_period: int = 20):
        self.lookback_period = lookback_period
        self.price_history = {}  # Store recent prices for each symbol
        self.signals = {}
        
    def update_price_history(self, symbol: str, price: float):
        """Update price history for a symbol"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append({
            'price': price,
            'timestamp': datetime.now()
        })
        
        # Keep only recent data
        if len(self.price_history[symbol]) > self.lookback_period * 2:
            self.price_history[symbol] = self.price_history[symbol][-self.lookback_period:]
    
    def calculate_signals(self, symbol: str) -> Dict:
        """Calculate trading signals based on available price history"""
        if symbol not in self.price_history or len(self.price_history[symbol]) < 5:
            return {'signal': 'HOLD', 'reason': 'Insufficient data'}
        
        prices = [p['price'] for p in self.price_history[symbol]]
        
        if len(prices) < self.lookback_period:
            return {'signal': 'HOLD', 'reason': f'Need {self.lookback_period} data points, have {len(prices)}'}
        
        # Calculate moving average
        ma = np.mean(prices[-self.lookback_period:])
        current_price = prices[-1]
        
        # Calculate percentiles
        recent_prices = prices[-min(10, len(prices)):]
        percentile_25 = np.percentile(recent_prices, 25)
        percentile_75 = np.percentile(recent_prices, 75)
        
        # Generate signals
        signal = 'HOLD'
        reason = ''
        
        if current_price < percentile_25:
            signal = 'BUY'
            reason = f'Price ({current_price:.2f}) below 25th percentile ({percentile_25:.2f})'
        elif current_price > percentile_75:
            signal = 'SELL'
            reason = f'Price ({current_price:.2f}) above 75th percentile ({percentile_75:.2f})'
        else:
            reason = f'Price ({current_price:.2f}) within normal range'
        
        return {
            'signal': signal,
            'reason': reason,
            'current_price': current_price,
            'moving_average': ma,
            'percentile_25': percentile_25,
            'percentile_75': percentile_75,
            'data_points': len(prices)
        }

class LiveTradingSystem:
    """Main live trading system"""
    
    def __init__(self, client_code: str, token_id: str, symbols: List[str]):
        self.collector = LiveDataCollector(client_code, token_id)
        self.strategy = LiveMeanReversionStrategy()
        self.symbols = symbols
        self.is_running = False
        self.trading_log = []
        
    def start_monitoring(self, interval: int = 60):
        """Start live monitoring"""
        logger.info(f"Starting live monitoring for {len(self.symbols)} symbols")
        self.is_running = True
        
        while self.is_running:
            try:
                self._monitor_cycle()
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                time.sleep(interval)
    
    def _monitor_cycle(self):
        """Single monitoring cycle"""
        logger.info("=" * 50)
        logger.info(f"Monitoring Cycle - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 50)
        
        # Get account info
        account_info = self.collector.get_account_info()
        if account_info:
            logger.info(f"Account Balance: {account_info.get('balance', 'N/A')}")
        
        # Try to collect live data
        live_data = self.collector.collect_live_data(self.symbols)
        
        if not live_data:
            logger.warning("No live data available - this is expected without Data APIs subscription")
            logger.info("Available API methods:")
            methods = self.collector.get_available_methods()
            for method in methods:
                logger.info(f"  - {method}")
            return
        
        # Process each symbol
        for symbol, data in live_data.items():
            logger.info(f"\nProcessing {symbol}:")
            logger.info(f"  Data type: {data.get('type', 'unknown')}")
            
            # Extract price if possible
            price = self._extract_price(data)
            if price:
                self.strategy.update_price_history(symbol, price)
                signal = self.strategy.calculate_signals(symbol)
                
                logger.info(f"  Current Price: {price:.2f}")
                logger.info(f"  Signal: {signal['signal']}")
                logger.info(f"  Reason: {signal['reason']}")
                
                # Log trading signal
                self._log_signal(symbol, signal)
            else:
                logger.info(f"  Could not extract price from data")
    
    def _extract_price(self, data: Dict) -> Optional[float]:
        """Extract price from various data formats"""
        try:
            if data.get('type') == 'historical' and hasattr(data['data'], 'iloc'):
                # DataFrame format
                df = data['data']
                if 'Close' in df.columns:
                    return float(df['Close'].iloc[-1])
                elif 'CLOSE' in df.columns:
                    return float(df['CLOSE'].iloc[-1])
                elif 'close' in df.columns:
                    return float(df['close'].iloc[-1])
            
            elif data.get('type') == 'live':
                # Live data format
                live_data = data['data']
                if isinstance(live_data, dict):
                    # Try common price field names
                    for field in ['ltp', 'close', 'price', 'last_price']:
                        if field in live_data:
                            return float(live_data[field])
                
                elif isinstance(live_data, (int, float)):
                    return float(live_data)
            
        except Exception as e:
            logger.debug(f"Error extracting price: {e}")
        
        return None
    
    def _log_signal(self, symbol: str, signal: Dict):
        """Log trading signal"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'signal': signal['signal'],
            'reason': signal['reason'],
            'current_price': signal.get('current_price'),
            'moving_average': signal.get('moving_average'),
            'data_points': signal.get('data_points')
        }
        
        self.trading_log.append(log_entry)
        
        # Save to file
        with open('data/live_trading_signals.json', 'w') as f:
            json.dump(self.trading_log, f, indent=2)
    
    def stop_monitoring(self):
        """Stop live monitoring"""
        self.is_running = False
        logger.info("Live monitoring stopped")
    
    def get_trading_summary(self) -> Dict:
        """Get summary of trading signals"""
        if not self.trading_log:
            return {'message': 'No trading signals yet'}
        
        signals = [log['signal'] for log in self.trading_log]
        buy_signals = signals.count('BUY')
        sell_signals = signals.count('SELL')
        hold_signals = signals.count('HOLD')
        
        return {
            'total_signals': len(signals),
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'hold_signals': hold_signals,
            'latest_signals': self.trading_log[-5:] if len(self.trading_log) >= 5 else self.trading_log
        }

def main():
    """Main function to run live trading system"""
    print("=" * 60)
    print("LIVE DATA ONLY TRADING SYSTEM")
    print("=" * 60)
    print("This system works with basic Dhan API access")
    print("(No historical data subscription required)")
    print()
    
    try:
        from config.dhan_config import DHAN_CLIENT_CODE, DHAN_TOKEN_ID, TRADING_SYMBOLS
        
        # Use first 5 symbols for testing
        test_symbols = TRADING_SYMBOLS[:5]
        
        print(f"Client Code: {DHAN_CLIENT_CODE}")
        print(f"Test Symbols: {test_symbols}")
        print()
        
        # Initialize system
        trading_system = LiveTradingSystem(
            client_code=DHAN_CLIENT_CODE,
            token_id=DHAN_TOKEN_ID,
            symbols=test_symbols
        )
        
        print("Starting live monitoring...")
        print("Press Ctrl+C to stop")
        print()
        
        # Start monitoring
        trading_system.start_monitoring(interval=30)  # Check every 30 seconds
        
    except KeyboardInterrupt:
        print("\nStopping live trading system...")
    except Exception as e:
        print(f"Error: {e}")
        print("Please check your Dhan API credentials in dhan_config.py")

if __name__ == "__main__":
    main() 