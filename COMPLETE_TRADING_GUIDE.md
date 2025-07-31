# 🎯 Mean Reversion Trading Algorithm - Complete Setup Guide

## 📊 Current Status & Solutions

### ✅ **What's Working Now**

1. **✅ Demo Mode**: Complete algorithm testing with synthetic data
2. **✅ Paper Trading**: Live simulation without real money
3. **✅ Quick Test**: Auto-fallback to demo mode when API fails
4. **✅ Strategy Logic**: Full mean reversion implementation

### ❌ **What Needs Real Data API**

- **Historical Backtesting**: Requires Dhan Data API subscription
- **Live Trading**: Requires Dhan Data API subscription

---

## 🚀 Available Trading Modes

### 1. **Demo Mode** (No API Required)
```bash
python run.py --demo
```
- ✅ Tests complete algorithm logic
- ✅ Uses realistic synthetic data
- ✅ Full backtesting reports
- ✅ Perfect for development

### 2. **Paper Trading with Demo Data** (No API Required)
```bash
python run.py --paper-demo
```
- ✅ Simulates live trading
- ✅ Order management system
- ✅ Portfolio tracking
- ✅ P&L calculations
- ✅ No real money involved

### 3. **Paper Trading with Real Data** (Requires Dhan Data API)
```bash
python run.py --paper-trading
```
- 🔄 Uses live market prices
- 🔄 Real-time trading signals
- ❌ **Currently blocked by DH-902 error**

### 4. **Quick Test**
```bash
python run.py --quick-test
```
- ✅ Tests 5 stocks quickly
- ✅ Auto-fallback to demo mode
- ✅ Validates strategy logic

---

## 📈 Mean Reversion Strategy Explained

### **Core Logic**
1. **Calculate 21-day moving average** for each stock
2. **Calculate price-to-MA ratio**: `current_price / moving_average`
3. **Generate signals based on percentiles**:
   - **SELL** when ratio > 95th percentile (price too high)
   - **BUY** when ratio < 5th percentile (price too low)
4. **Hold positions** until next signal

### **Strategy Parameters**
- **Moving Average Period**: 21 days
- **Short Signal**: 95th percentile (overbought)
- **Long Signal**: 5th percentile (oversold)
- **Position Size**: 5% of portfolio per stock

### **Why Some Stocks Outperform**
Mean reversion works best for:
- ✅ **Volatile but range-bound stocks**
- ✅ **Stocks with strong mean-reverting patterns**
- ✅ **Sideways trending markets**

---

## 🛠️ Next Steps for Real Trading

### **Option 1: Subscribe to Dhan Data APIs**
1. **Log into your Dhan account**
2. **Navigate to API section**
3. **Subscribe to Data APIs** (costs ₹1000-2000/month typically)
4. **Ensure historical data access is included**
5. **Then run**: `python run.py --paper-trading`

### **Option 2: Alternative Data Sources**
Consider integrating with:
- **Yahoo Finance** (free but limited)
- **Alpha Vantage** (free tier available)
- **Polygon.io** (paid but comprehensive)

---

## 🔧 Current File Structure

```
src/
├── demo_data_generator.py      # Synthetic data generation
├── paper_trading_system.py     # Paper trading engine
├── live_paper_trading.py       # Real-time paper trading
├── mean_reversion_strategy.py  # Core strategy logic
├── data_loader_async.py        # Dhan API integration
└── live_trading_system.py      # Live trading framework

data/
├── demo_results/               # Demo backtest results
├── paper_trading/              # Paper trading logs
└── results/                    # Real data results (when available)
```

---

## 📊 Paper Trading Features

### **Order Management**
- ✅ Buy/Sell order placement
- ✅ Slippage simulation (0.05%)
- ✅ Transaction costs (0.1%)
- ✅ Position tracking

### **Portfolio Management**
- ✅ Real-time P&L calculation
- ✅ Position sizing (5% per stock)
- ✅ Capital allocation
- ✅ Risk management

### **Reporting**
- ✅ Trade logs
- ✅ Portfolio history
- ✅ Performance metrics
- ✅ Daily/hourly reports

---

## 🎮 Try It Now

### **1. Test the Strategy Logic**
```bash
python run.py --demo
```

### **2. Test Paper Trading**
```bash
python run.py --paper-demo
```

### **3. Quick Validation**
```bash
python run.py --quick-test
```

---

## 🔮 When You Get Real Data Access

### **Historical Backtesting**
```bash
python run.py                    # Full historical analysis
python run.py --backtest        # Backtesting only
```

### **Live Paper Trading**
```bash
python run.py --paper-trading   # Paper trading with real prices
```

### **Live Trading** (When Ready)
```bash
python run.py --live            # Real money trading
```

---

## 📋 Summary

✅ **Current Capabilities**:
- Complete mean reversion strategy implementation
- Paper trading simulation system
- Comprehensive demo mode
- Automated fallback mechanisms

🔄 **Next Steps**:
- Subscribe to Dhan Data APIs for real data
- Test paper trading with live market prices
- Optimize strategy parameters
- Consider alternative data sources

❌ **Current Limitation**:
- Real market data requires API subscription (DH-902 error)

Your algorithm is **fully functional** for testing and development. Once you get the Data API subscription, you'll have complete real-time trading capabilities!
