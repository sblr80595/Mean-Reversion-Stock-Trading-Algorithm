# Dhan API Configuration for Mean Reversion Trading Algorithm

# Dhan API Credentials
# Replace these with your actual Dhan API credentials
DHAN_CLIENT_CODE = "1103096874"
DHAN_TOKEN_ID = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzU2MzQ0MTU0LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMzA5Njg3NCJ9.4TO9wcVe9DrDetqkAUUcoV3QC0irv1QM6Es4xmKv3MIib20awt6Ir7BOoyHA5ilxf4uYAWiCgnY2XE-R-1w3kw"

# Trading Configuration
TRADING_SYMBOLS = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
    'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'AXISBANK',
    'KOTAKBANK', 'LT', 'MARUTI', 'WIPRO', 'TECHM',
    'SUNPHARMA', 'TATAMOTORS', 'TATASTEEL', 'ULTRACEMCO', 'NESTLEIND'
]

# Exchange settings
EXCHANGE = 'NSE'  # NSE for stocks, INDEX for indices
TIMEFRAME = 'DAY'  # 1, 5, 15, 60, DAY

# Trading Parameters
CHECK_INTERVAL = 300  # Check for signals every 5 minutes
MAX_POSITION_SIZE = 0.1  # Maximum 10% allocation per stock
STOP_LOSS_PERCENTAGE = 0.05  # 5% stop loss
TAKE_PROFIT_PERCENTAGE = 0.15  # 15% take profit

# Order Settings
ORDER_TYPE = 'MARKET'  # MARKET or LIMIT
ENABLE_DEBUG = True  # Enable debug mode for API calls

# Risk Management
MAX_DAILY_LOSS = 0.02  # Maximum 2% daily loss
MAX_PORTFOLIO_RISK = 0.05  # Maximum 5% portfolio risk
POSITION_SIZING_METHOD = 'KELLY'  # KELLY, FIXED, or VOLATILITY

# Notification Settings
ENABLE_TELEGRAM_ALERTS = False
TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"

# Logging Settings
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = 'trading_log.txt'
SAVE_TRADES_TO_CSV = True
TRADE_LOG_FILE = 'trades.csv'

# Performance Tracking
TRACK_PERFORMANCE = True
PERFORMANCE_FILE = 'performance.json'
DAILY_REPORT = True
WEEKLY_REPORT = True

# Market Hours (IST)
MARKET_OPEN = "09:15"
MARKET_CLOSE = "15:30"
PRE_MARKET_START = "09:00"
POST_MARKET_END = "15:45"

# Strategy Parameters (inherited from main config)
from config.config import (
    MOVING_AVERAGE_PERIOD,
    SHORT_PERCENTILE,
    LONG_PERCENTILE
)

# Additional Dhan-specific parameters
DHAN_API_TIMEOUT = 30  # API timeout in seconds
DHAN_RETRY_ATTEMPTS = 3  # Number of retry attempts for failed API calls
DHAN_RETRY_DELAY = 5  # Delay between retry attempts in seconds

# Order Management
AUTO_CANCEL_ORDERS = True  # Cancel pending orders at market close
CANCEL_ORDERS_AT_CLOSE = True  # Cancel all orders at market close
MAX_PENDING_ORDERS = 10  # Maximum number of pending orders

# Data Management
CACHE_HISTORICAL_DATA = True  # Cache historical data to reduce API calls
CACHE_DURATION = 3600  # Cache duration in seconds (1 hour)
SAVE_MARKET_DATA = True  # Save market data to local files

# Error Handling
CONTINUE_ON_ERROR = True  # Continue trading even if some API calls fail
LOG_ERRORS_TO_FILE = True  # Log errors to separate file
SEND_ERROR_ALERTS = False  # Send error alerts via Telegram

# Testing Mode
TESTING_MODE = False  # Set to True for paper trading
PAPER_TRADING_BALANCE = 100000  # Paper trading balance in INR
SIMULATE_ORDERS = False  # Simulate orders without placing them

# Portfolio Management
REBALANCE_PORTFOLIO = False  # Rebalance portfolio periodically
REBALANCE_FREQUENCY = 'WEEKLY'  # DAILY, WEEKLY, MONTHLY
TARGET_ALLOCATION = {
    'RELIANCE': 0.15,
    'TCS': 0.12,
    'HDFCBANK': 0.10,
    'INFY': 0.10,
    'ICICIBANK': 0.08,
    'HINDUNILVR': 0.08,
    'ITC': 0.08,
    'SBIN': 0.08,
    'BHARTIARTL': 0.06,
    'AXISBANK': 0.06
}

# Advanced Settings
USE_SMART_ORDER_ROUTING = False  # Use smart order routing
ENABLE_ALGO_TRADING = False  # Enable algorithmic trading features
USE_STOP_ORDERS = True  # Use stop orders for risk management
USE_BRACKET_ORDERS = False  # Use bracket orders for take profit and stop loss

# Data Validation
VALIDATE_MARKET_DATA = True  # Validate market data before using
MIN_DATA_POINTS = 50  # Minimum data points required for analysis
MAX_DATA_AGE = 86400  # Maximum age of data in seconds (24 hours)

# Performance Metrics
CALCULATE_SHARPE_RATIO = True
CALCULATE_MAX_DRAWDOWN = True
CALCULATE_WIN_RATE = True
CALCULATE_PROFIT_FACTOR = True

# Reporting
GENERATE_DAILY_REPORT = True
GENERATE_WEEKLY_REPORT = True
GENERATE_MONTHLY_REPORT = True
REPORT_FORMAT = 'HTML'  # HTML, PDF, CSV

# Backup and Recovery
BACKUP_TRADING_DATA = True
BACKUP_FREQUENCY = 'DAILY'  # DAILY, WEEKLY
BACKUP_RETENTION_DAYS = 30  # Keep backups for 30 days 