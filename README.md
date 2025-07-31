# Mean Reversion Stock Trading Algorithm

A sophisticated algorithmic trading system that implements mean reversion strategies for Nifty 50 stocks using the Dhan API.

## 🏗️ Project Structure

```
Mean-Reversion-Stock-Trading-Algorithm/
├── config/                     # Configuration files
│   ├── __init__.py
│   ├── config.py              # Main algorithm configuration
│   ├── dhan_config.py         # Dhan API credentials
│   └── rate_limit_config.py   # Rate limiting settings
├── src/                       # Source code
│   ├── __init__.py
│   ├── data_loader.py         # Synchronous data loader
│   ├── data_loader_async.py   # Async data loader with rate limiting
│   ├── mean_reversion_strategy.py  # Core trading strategy
│   ├── dhan_trading_system.py # Live trading system
│   └── live_trading_system.py # Live data only system
├── data/                      # Data storage
│   ├── Dependencies/          # API dependencies
│   ├── results/              # Backtest results
│   └── live_trading_signals.json
├── logs/                     # Log files
├── tests/                    # Test files
├── docs/                     # Documentation
├── main.py                   # Main execution script
├── requirements.txt          # Python dependencies
├── requirements_minimal.txt  # Minimal dependencies
├── INSTALLATION.md          # Installation guide
├── RATE_LIMITING_GUIDE.md   # Rate limiting guide
└── .gitignore               # Git ignore rules
```

## 🚀 Features

- **Mean Reversion Strategy**: Based on Bollinger Bands and percentile analysis
- **Rate Limiting**: Robust API rate limiting with exponential backoff
- **Parallel Processing**: Efficient data fetching with configurable workers
- **Live Trading**: Real-time monitoring and signal generation
- **Backtesting**: Comprehensive strategy backtesting with performance metrics
- **Visualization**: Interactive charts and performance analysis
- **Error Handling**: Graceful error handling and recovery

## 📋 Prerequisites

- Python 3.8+
- Dhan Trading Account with API access
- Required Python packages (see requirements.txt)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Mean-Reversion-Stock-Trading-Algorithm
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API credentials**:
   - Copy `config/dhan_config.py.example` to `config/dhan_config.py`
   - Update with your Dhan API credentials

## ⚙️ Configuration

### Main Configuration (`config/config.py`)
- Trading symbols (Nifty 50)
- Strategy parameters
- Date ranges
- Performance settings

### Dhan API Configuration (`config/dhan_config.py`)
- API credentials
- Trading parameters
- Risk management settings

### Rate Limiting Configuration (`config/rate_limit_config.py`)
- API rate limits
- Retry strategies
- Batch processing settings

## 🎯 Usage

### Running the Main Algorithm
```bash
python main.py
```

### Quick Test Mode
```bash
python main.py --quick-test
```

### Live Trading System
```bash
python src/live_trading_system.py
```

## 📊 Strategy Overview

The algorithm implements a mean reversion strategy based on:

1. **Moving Average**: Calculates rolling mean of prices
2. **Percentile Analysis**: Identifies overbought/oversold conditions
3. **Signal Generation**: Buy when price is below 5th percentile, sell when above 95th percentile
4. **Position Management**: Maintains positions until signal reversal

## 🔧 Rate Limiting

The system includes sophisticated rate limiting to handle Dhan API constraints:

- **Exponential Backoff**: Progressive delays on rate limit errors
- **Batch Processing**: Processes symbols in configurable batches
- **Parallel Workers**: Configurable number of concurrent requests
- **Error Recovery**: Automatic retry with intelligent delays

## 📈 Performance Metrics

The backtesting system provides:

- **Total Returns**: Strategy vs Buy & Hold
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Worst peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Volatility**: Standard deviation of returns

## 🛡️ Risk Management

- **Position Sizing**: Configurable allocation per stock
- **Stop Loss**: Automatic stop loss implementation
- **Portfolio Limits**: Maximum portfolio risk settings
- **Daily Loss Limits**: Maximum daily loss protection

## 📝 Logging

All activities are logged to:
- `logs/live_trading.log` - Live trading activities
- Console output - Real-time monitoring
- `data/results/` - Backtest results and reports

## 🔍 Troubleshooting

### Common Issues

1. **Rate Limit Errors**: 
   - Check `config/rate_limit_config.py`
   - Reduce batch size or increase delays

2. **API Access Errors**:
   - Verify Dhan API credentials
   - Check subscription level for Data APIs

3. **Import Errors**:
   - Ensure virtual environment is activated
   - Check Python path configuration

### Getting Help

- Check the logs in `logs/` directory
- Review `RATE_LIMITING_GUIDE.md` for API issues
- Consult `INSTALLATION.md` for setup problems

## 📄 License

This project is for educational and research purposes. Please ensure compliance with your broker's terms of service and local regulations.

## ⚠️ Disclaimer

This software is provided "as is" without warranty. Trading involves risk, and past performance does not guarantee future results. Use at your own risk and ensure proper risk management.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues related to:
- **Dhan API**: Contact Dhan support
- **Code Issues**: Open an issue on GitHub
- **Configuration**: Check the documentation in `docs/`
