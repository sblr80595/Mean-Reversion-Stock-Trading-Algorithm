# Configuration file for Nifty 50 Mean Reversion Trading Algorithm

# Nifty 50 stock symbols (using Dhan API format)
NIFTY_50_SYMBOLS = [
    'ADANIENT', 'ADANIPORTS', 'APOLLOHOSP', 'ASIANPAINT', 'AXISBANK',
    'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BHARTIARTL',
    'BPCL', 'BRITANNIA', 'CIPLA', 'COALINDIA', 'DIVISLAB',
    'DRREDDY', 'EICHERMOT', 'GRASIM', 'HCLTECH', 'HDFC',
    'HDFCBANK', 'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'HINDUNILVR',
    'ICICIBANK', 'INDUSINDBK', 'INFY', 'ITC', 'JSWSTEEL',
    'KOTAKBANK', 'LT', 'M&M', 'MARUTI', 'NESTLEIND',
    'NTPC', 'ONGC', 'POWERGRID', 'RELIANCE', 'SBILIFE',
    'SBIN', 'SUNPHARMA', 'TATACONSUM', 'TATAMOTORS', 'TATASTEEL',
    'TECHM', 'TITAN', 'ULTRACEMCO', 'UPL', 'WIPRO'
]

# Trading parameters
MOVING_AVERAGE_PERIOD = 21
SHORT_PERCENTILE = 95  # Sell when ratio > 95th percentile
LONG_PERCENTILE = 5    # Buy when ratio < 5th percentile

# Date range for backtesting
START_DATE = '2023-01-01'  # More recent data for testing
END_DATE = '2024-12-31'    # Include current year

# Risk management
MAX_POSITION_SIZE = 0.1  # Maximum 10% allocation per stock
STOP_LOSS_PERCENTAGE = 0.05  # 5% stop loss
TAKE_PROFIT_PERCENTAGE = 0.15  # 15% take profit

# Performance metrics
RISK_FREE_RATE = 0.05  # 5% risk-free rate for Sharpe ratio calculation 