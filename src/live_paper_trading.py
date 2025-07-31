#!/usr/bin/env python3
"""
Real-time Paper Trading System with Live Market Data
Integrates with Dhan API for real market prices
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import schedule
import threading

from src.paper_trading_system import PaperMeanReversionTrader, PaperTradingEngine
import config.config as cfg

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/live_paper_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealTimePaperTrader:
    """
    Real-time paper trading system using live market data
    """
    
    def __init__(self, symbols: List[str], initial_capital: float = 100000):
        self.symbols = symbols
        self.trader = PaperMeanReversionTrader(symbols, initial_capital)
        self.dhan_client = None
        self.is_running = False
        self.market_hours = {'start': 9, 'end': 15}  # 9:15 AM to 3:30 PM IST
        
        # Initialize Dhan connection
        self._initialize_dhan()
    
    def _initialize_dhan(self):
        """Initialize Dhan API connection"""
        try:
            from config.dhan_config import DHAN_CLIENT_CODE, DHAN_TOKEN_ID
            from Dhan_Tradehull import Tradehull
            
            self.dhan_client = Tradehull(DHAN_CLIENT_CODE, DHAN_TOKEN_ID)
            logger.info("✓ Connected to Dhan API for live data")
            
        except ImportError:
            logger.error("Dhan credentials not found. Please configure config/dhan_config.py")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Dhan API: {e}")
            return False
        
        return True
    
    def get_live_prices(self) -> Dict[str, float]:
        """
        Get current market prices for all symbols
        This uses whatever data is available from Dhan API
        """
        prices = {}
        
        if not self.dhan_client:
            logger.warning("No Dhan connection available")
            return prices
        
        for symbol in self.symbols:
            try:
                # Try to get current price using available methods
                price = self._get_symbol_price(symbol)
                if price:
                    prices[symbol] = price
                    
            except Exception as e:
                logger.debug(f"Could not get price for {symbol}: {e}")
        
        return prices
    
    def _get_symbol_price(self, symbol: str) -> Optional[float]:
        """
        Try to get current price for a symbol using available Dhan methods
        """
        try:
            # Method 1: Try get_ltp_data if available
            if hasattr(self.dhan_client, 'get_ltp_data'):
                data = self.dhan_client.get_ltp_data([symbol])
                if data and isinstance(data, dict):
                    if symbol in data:
                        return float(data[symbol].get('ltp', 0))
            
            # Method 2: Try get_quote_data if available
            if hasattr(self.dhan_client, 'get_quote_data'):
                data = self.dhan_client.get_quote_data(symbol, 'NSE')
                if data and isinstance(data, dict):
                    return float(data.get('ltp', 0))
            
            # Method 3: Try any historical data for recent price
            if hasattr(self.dhan_client, 'get_historical_data'):
                data = self.dhan_client.get_historical_data(
                    tradingsymbol=symbol,
                    exchange='NSE',
                    timeframe='1',  # 1-minute data
                    debug="NO"
                )
                if data is not None:
                    # If it's a DataFrame, get the latest close price
                    if hasattr(data, 'iloc') and len(data) > 0:
                        return float(data['CLOSE'].iloc[-1])
                    elif isinstance(data, list) and len(data) > 0:
                        return float(data[-1].get('close', 0))
            
        except Exception as e:
            logger.debug(f"Error getting price for {symbol}: {e}")
        
        return None
    
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        
        # Market hours: 9:15 AM to 3:30 PM IST (Monday to Friday)
        if now.weekday() >= 5:  # Weekend
            return False
        
        market_start = self.market_hours['start'] * 60 + 15  # 9:15 AM in minutes
        market_end = self.market_hours['end'] * 60 + 30     # 3:30 PM in minutes
        current_time = current_hour * 60 + current_minute
        
        return market_start <= current_time <= market_end
    
    def run_trading_cycle(self):
        """Run one trading cycle - get prices and update strategy"""
        if not self.is_market_open():
            logger.info("Market is closed. Skipping trading cycle.")
            return
        
        logger.info("Running trading cycle...")
        
        # Get live prices
        prices = self.get_live_prices()
        
        if not prices:
            logger.warning("No live prices available")
            return
        
        logger.info(f"Got prices for {len(prices)} symbols: {prices}")
        
        # Update trader with new prices
        self.trader.update_prices(prices)
        
        # Log portfolio status
        summary = self.trader.engine.get_portfolio_summary()
        logger.info(f"Portfolio: ₹{summary['total_value']:,.2f} | P&L: ₹{summary['total_pnl']:,.2f} ({summary['pnl_percentage']:.2f}%) | Positions: {summary['num_positions']}")
        
        # Save state periodically
        self.trader.engine.save_state()
    
    def start_live_trading(self):
        """Start live paper trading"""
        logger.info("=" * 60)
        logger.info("STARTING LIVE PAPER TRADING")
        logger.info("=" * 60)
        logger.info(f"Symbols: {self.symbols}")
        logger.info(f"Initial Capital: ₹{self.trader.engine.initial_capital:,.2f}")
        logger.info(f"Market Hours: {self.market_hours['start']}:15 - {self.market_hours['end']}:30 IST")
        logger.info("Strategy: Mean Reversion with Live Market Data")
        logger.info("=" * 60)
        
        self.is_running = True
        
        # Schedule trading cycles
        schedule.every(5).minutes.do(self.run_trading_cycle)  # Run every 5 minutes
        schedule.every().hour.do(self._hourly_report)        # Hourly reports
        schedule.every().day.at("15:45").do(self._daily_report)  # End of day report
        
        # Initial cycle
        self.run_trading_cycle()
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            logger.info("Live paper trading stopped by user")
        
        finally:
            self.stop_trading()
    
    def _hourly_report(self):
        """Generate hourly trading report"""
        summary = self.trader.engine.get_portfolio_summary()
        logger.info("=" * 40)
        logger.info("HOURLY REPORT")
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Portfolio Value: ₹{summary['total_value']:,.2f}")
        logger.info(f"P&L: ₹{summary['total_pnl']:,.2f} ({summary['pnl_percentage']:.2f}%)")
        logger.info(f"Active Positions: {summary['num_positions']}")
        logger.info(f"Total Trades: {summary['num_trades']}")
        logger.info("=" * 40)
    
    def _daily_report(self):
        """Generate end-of-day report"""
        summary = self.trader.engine.get_portfolio_summary()
        
        logger.info("=" * 60)
        logger.info("END OF DAY REPORT")
        logger.info("=" * 60)
        logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        logger.info(f"Initial Capital: ₹{summary['initial_capital']:,.2f}")
        logger.info(f"Final Value: ₹{summary['total_value']:,.2f}")
        logger.info(f"Daily P&L: ₹{summary['total_pnl']:,.2f}")
        logger.info(f"Return: {summary['pnl_percentage']:.2f}%")
        logger.info(f"Trades Today: {summary['num_trades']}")
        logger.info(f"Active Positions: {summary['num_positions']}")
        
        # List active positions
        if self.trader.engine.positions:
            logger.info("\nActive Positions:")
            for symbol, pos in self.trader.engine.positions.items():
                logger.info(f"  {symbol}: {pos.quantity} shares @ ₹{pos.avg_price:.2f} | P&L: ₹{pos.unrealized_pnl:.2f}")
        
        logger.info("=" * 60)
        
        # Save final state
        self.trader.engine.save_state()
    
    def stop_trading(self):
        """Stop live trading"""
        self.is_running = False
        logger.info("Paper trading stopped")
        
        # Final report
        self._daily_report()

def main():
    """Main function for live paper trading"""
    
    # Use first 10 symbols from config for testing
    symbols = cfg.NIFTY_50_SYMBOLS[:10]
    
    # Initialize real-time paper trader
    trader = RealTimePaperTrader(symbols, initial_capital=100000)
    
    if trader.dhan_client is None:
        print("❌ Could not connect to Dhan API")
        print("📝 Solutions:")
        print("  1. Subscribe to Dhan Data APIs")
        print("  2. Check your Dhan credentials in config/dhan_config.py")
        print("  3. Run with demo data: python run.py --demo")
        return
    
    # Start live trading
    trader.start_live_trading()

if __name__ == "__main__":
    main()
