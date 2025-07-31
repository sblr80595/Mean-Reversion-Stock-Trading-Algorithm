#!/usr/bin/env python3
"""
Paper Trading System for Mean Reversion Strategy
Simulates real trading without actual money
"""

import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/paper_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"

@dataclass
class Order:
    id: str
    symbol: str
    order_type: OrderType
    quantity: int
    price: float
    timestamp: datetime
    status: OrderStatus = OrderStatus.PENDING
    execution_price: Optional[float] = None
    execution_time: Optional[datetime] = None

@dataclass
class Position:
    symbol: str
    quantity: int
    avg_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float

class PaperTradingEngine:
    """
    Paper trading engine that simulates real trading
    """
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}  # symbol -> Position
        self.orders = []  # List of orders
        self.trades = []  # Executed trades
        self.portfolio_history = []
        
        # Trading parameters
        self.transaction_cost = 0.001  # 0.1% transaction cost
        self.slippage = 0.0005  # 0.05% slippage
        
        # Create directories
        os.makedirs('data/paper_trading', exist_ok=True)
        
        logger.info(f"Paper Trading Engine initialized with capital: ₹{initial_capital:,.2f}")
    
    def place_order(self, symbol: str, order_type: OrderType, quantity: int, price: float) -> str:
        """Place a paper trading order"""
        order_id = f"ORDER_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.orders)}"
        
        order = Order(
            id=order_id,
            symbol=symbol,
            order_type=order_type,
            quantity=quantity,
            price=price,
            timestamp=datetime.now()
        )
        
        self.orders.append(order)
        logger.info(f"Order placed: {order_type.value} {quantity} {symbol} @ ₹{price:.2f}")
        
        # For paper trading, execute immediately with slippage
        self._execute_order(order)
        
        return order_id
    
    def _execute_order(self, order: Order):
        """Execute a paper trading order"""
        # Simulate slippage
        if order.order_type == OrderType.BUY:
            execution_price = order.price * (1 + self.slippage)
        else:
            execution_price = order.price * (1 - self.slippage)
        
        # Check if we have enough capital/shares
        total_cost = execution_price * order.quantity * (1 + self.transaction_cost)
        
        if order.order_type == OrderType.BUY:
            if total_cost > self.current_capital:
                logger.warning(f"Insufficient capital for order {order.id}")
                order.status = OrderStatus.CANCELLED
                return
        else:  # SELL
            current_position = self.positions.get(order.symbol)
            if not current_position or current_position.quantity < order.quantity:
                logger.warning(f"Insufficient shares for order {order.id}")
                order.status = OrderStatus.CANCELLED
                return
        
        # Execute the order
        order.status = OrderStatus.EXECUTED
        order.execution_price = execution_price
        order.execution_time = datetime.now()
        
        # Update positions and capital
        self._update_position(order)
        
        # Record trade
        trade = {
            'timestamp': order.execution_time,
            'symbol': order.symbol,
            'type': order.order_type.value,
            'quantity': order.quantity,
            'price': execution_price,
            'value': execution_price * order.quantity,
            'cost': total_cost,
            'order_id': order.id
        }
        self.trades.append(trade)
        
        logger.info(f"Order executed: {order.order_type.value} {order.quantity} {order.symbol} @ ₹{execution_price:.2f}")
    
    def _update_position(self, order: Order):
        """Update position after order execution"""
        symbol = order.symbol
        execution_price = order.execution_price or 0.0  # Handle None case
        
        if order.order_type == OrderType.BUY:
            if symbol in self.positions:
                # Update existing position
                pos = self.positions[symbol]
                total_value = pos.avg_price * pos.quantity + execution_price * order.quantity
                total_quantity = pos.quantity + order.quantity
                pos.avg_price = total_value / total_quantity
                pos.quantity = total_quantity
            else:
                # Create new position
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=order.quantity,
                    avg_price=execution_price,
                    current_price=execution_price,
                    unrealized_pnl=0.0,
                    realized_pnl=0.0
                )
            
            # Reduce capital
            total_cost = execution_price * order.quantity * (1 + self.transaction_cost)
            self.current_capital -= total_cost
            
        else:  # SELL
            if symbol in self.positions:
                pos = self.positions[symbol]
                
                # Calculate realized P&L
                realized_pnl = (execution_price - pos.avg_price) * order.quantity
                pos.realized_pnl += realized_pnl
                
                # Update position
                pos.quantity -= order.quantity
                
                # Add capital
                total_value = execution_price * order.quantity * (1 - self.transaction_cost)
                self.current_capital += total_value
                
                # Remove position if quantity becomes 0
                if pos.quantity == 0:
                    del self.positions[symbol]
    
    def update_market_prices(self, price_data: Dict[str, float]):
        """Update current market prices for positions"""
        for symbol, price in price_data.items():
            if symbol in self.positions:
                pos = self.positions[symbol]
                pos.current_price = price
                pos.unrealized_pnl = (price - pos.avg_price) * pos.quantity
    
    def get_portfolio_value(self) -> float:
        """Calculate total portfolio value"""
        positions_value = sum(
            pos.quantity * pos.current_price 
            for pos in self.positions.values()
        )
        return self.current_capital + positions_value
    
    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary"""
        total_value = self.get_portfolio_value()
        total_pnl = total_value - self.initial_capital
        pnl_percentage = (total_pnl / self.initial_capital) * 100
        
        return {
            'timestamp': datetime.now().isoformat(),
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'positions_value': total_value - self.current_capital,
            'total_value': total_value,
            'total_pnl': total_pnl,
            'pnl_percentage': pnl_percentage,
            'num_positions': len(self.positions),
            'num_trades': len(self.trades)
        }
    
    def save_state(self):
        """Save current state to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save portfolio summary
        summary = self.get_portfolio_summary()
        self.portfolio_history.append(summary)
        
        with open(f'data/paper_trading/portfolio_history.json', 'w') as f:
            json.dump(self.portfolio_history, f, indent=2)
        
        # Save trades
        if self.trades:
            trades_df = pd.DataFrame(self.trades)
            trades_df.to_csv(f'data/paper_trading/trades_{timestamp}.csv', index=False)
        
        # Save positions
        if self.positions:
            positions_data = []
            for symbol, pos in self.positions.items():
                positions_data.append({
                    'symbol': symbol,
                    'quantity': pos.quantity,
                    'avg_price': pos.avg_price,
                    'current_price': pos.current_price,
                    'unrealized_pnl': pos.unrealized_pnl,
                    'realized_pnl': pos.realized_pnl
                })
            
            positions_df = pd.DataFrame(positions_data)
            positions_df.to_csv(f'data/paper_trading/positions_{timestamp}.csv', index=False)
        
        logger.info(f"Portfolio state saved - Total Value: ₹{summary['total_value']:,.2f}, P&L: ₹{summary['total_pnl']:,.2f} ({summary['pnl_percentage']:.2f}%)")

class PaperMeanReversionTrader:
    """
    Paper trading implementation of mean reversion strategy
    """
    
    def __init__(self, symbols: List[str], initial_capital: float = 100000):
        self.symbols = symbols
        self.engine = PaperTradingEngine(initial_capital)
        self.price_history = {symbol: [] for symbol in symbols}
        self.lookback_period = 21
        self.signal_threshold = 2.0  # Standard deviations
        self.position_size = 0.05  # 5% of portfolio per position
        
        logger.info(f"Paper Mean Reversion Trader initialized for {len(symbols)} symbols")
    
    def update_prices(self, price_data: Dict[str, float]):
        """Update price history and generate signals"""
        # Update price history
        for symbol, price in price_data.items():
            if symbol in self.price_history:
                self.price_history[symbol].append(price)
                # Keep only recent prices
                if len(self.price_history[symbol]) > self.lookback_period * 2:
                    self.price_history[symbol] = self.price_history[symbol][-self.lookback_period * 2:]
        
        # Update market prices in engine
        self.engine.update_market_prices(price_data)
        
        # Generate trading signals
        self._generate_signals(price_data)
    
    def _generate_signals(self, current_prices: Dict[str, float]):
        """Generate mean reversion trading signals"""
        for symbol, current_price in current_prices.items():
            if symbol not in self.price_history:
                continue
            
            prices = self.price_history[symbol]
            if len(prices) < self.lookback_period:
                continue
            
            # Calculate mean reversion signals
            recent_prices = np.array(prices[-self.lookback_period:])
            mean_price = np.mean(recent_prices)
            std_price = np.std(recent_prices)
            
            if std_price == 0:
                continue
            
            # Z-score (how many standard deviations from mean)
            z_score = (current_price - mean_price) / std_price
            
            # Trading logic
            portfolio_value = self.engine.get_portfolio_value()
            position_value = portfolio_value * self.position_size
            quantity = int(position_value / current_price)
            
            if quantity == 0:
                continue
            
            # Mean reversion signals
            if z_score > self.signal_threshold:
                # Price too high, SELL signal
                current_position = self.engine.positions.get(symbol)
                if current_position and current_position.quantity > 0:
                    self.engine.place_order(symbol, OrderType.SELL, 
                                          min(quantity, current_position.quantity), 
                                          current_price)
            
            elif z_score < -self.signal_threshold:
                # Price too low, BUY signal
                if self.engine.current_capital > position_value:
                    self.engine.place_order(symbol, OrderType.BUY, quantity, current_price)
    
    def run_simulation(self, price_data_stream):
        """Run paper trading simulation"""
        logger.info("Starting paper trading simulation...")
        
        for timestamp, price_data in price_data_stream:
            self.update_prices(price_data)
            
            # Log portfolio status every hour
            if datetime.now().minute == 0:
                summary = self.engine.get_portfolio_summary()
                logger.info(f"Portfolio Update - Value: ₹{summary['total_value']:,.2f}, P&L: {summary['pnl_percentage']:.2f}%")
            
            # Save state periodically
            if len(self.engine.trades) % 10 == 0 and len(self.engine.trades) > 0:
                self.engine.save_state()
            
            time.sleep(1)  # Small delay for simulation

def create_sample_price_stream():
    """Create sample price data for testing"""
    # This would be replaced with real market data
    symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK']
    base_prices = {'RELIANCE': 2500.0, 'TCS': 3500.0, 'HDFCBANK': 1600.0, 'INFY': 1400.0, 'ICICIBANK': 950.0}
    
    for i in range(100):  # 100 price updates
        price_data = {}
        for symbol in symbols:
            # Simulate price movement
            change = np.random.normal(0, 0.02)  # 2% volatility
            new_price = base_prices[symbol] * (1 + change)
            base_prices[symbol] = new_price
            price_data[symbol] = new_price
        
        yield datetime.now(), price_data
        time.sleep(0.1)

def main():
    """Main function for paper trading"""
    symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK']
    
    # Initialize paper trader
    trader = PaperMeanReversionTrader(symbols, initial_capital=100000)
    
    print("=" * 60)
    print("PAPER TRADING - MEAN REVERSION STRATEGY")
    print("=" * 60)
    print(f"Symbols: {symbols}")
    print(f"Initial Capital: ₹{trader.engine.initial_capital:,.2f}")
    print("Strategy: Mean Reversion with Z-score signals")
    print("=" * 60)
    
    try:
        # Create sample price stream (replace with real data)
        price_stream = create_sample_price_stream()
        trader.run_simulation(price_stream)
        
    except KeyboardInterrupt:
        logger.info("Paper trading stopped by user")
    
    finally:
        # Final save and summary
        trader.engine.save_state()
        summary = trader.engine.get_portfolio_summary()
        
        print("\n" + "=" * 60)
        print("PAPER TRADING SUMMARY")
        print("=" * 60)
        print(f"Initial Capital: ₹{summary['initial_capital']:,.2f}")
        print(f"Final Value: ₹{summary['total_value']:,.2f}")
        print(f"Total P&L: ₹{summary['total_pnl']:,.2f}")
        print(f"Return: {summary['pnl_percentage']:.2f}%")
        print(f"Number of Trades: {summary['num_trades']}")
        print(f"Active Positions: {summary['num_positions']}")
        print("=" * 60)

if __name__ == "__main__":
    main()
