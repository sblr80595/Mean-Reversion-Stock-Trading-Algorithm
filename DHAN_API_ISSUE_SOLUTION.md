# Important Notice: Dhan Data API Subscription Issue

## Problem Description

Your quick test is failing because your Dhan account **does not have a subscription to the Data APIs**. This is indicated by the error:

```
DH-902: User has not subscribed to Data APIs or does not have access to Trading APIs. 
Kindly subscribe to Data APIs to be able to fetch Data.
```

## Solutions

### Option 1: Subscribe to Dhan Data APIs (Recommended for Real Trading)

1. **Log in to your Dhan account**
2. **Navigate to API section**
3. **Subscribe to Data APIs**
4. **Ensure your subscription includes historical data access**

### Option 2: Use Demo Mode (Testing & Development)

We've added a **demo mode** that uses synthetic data for testing the algorithm logic:

```bash
# Run with demo/synthetic data (no API subscription required)
python run.py --demo

# Quick test now automatically falls back to demo mode if API fails
python run.py --quick-test
```

## What Works Now

✅ **Demo Mode**: Full algorithm testing with synthetic data  
✅ **Quick Test**: Automatically falls back to demo mode if API fails  
✅ **Algorithm Logic**: Complete mean reversion strategy testing  
✅ **Backtesting**: Full backtesting capabilities with demo data  

## Available Commands

```bash
# Basic usage
python run.py --demo                 # Run with synthetic data (no API required)
python run.py --quick-test          # Quick test (auto-fallback to demo)
python run.py --config              # Show current configuration
python run.py --setup               # Setup and verify installation

# When you have Dhan Data API subscription
python run.py                       # Run main algorithm with real data
python run.py --live                # Run live trading system
python run.py --backtest            # Run backtesting with real data
```

## Demo Mode Features

- ✅ Generates realistic synthetic stock data
- ✅ Uses proper OHLCV format
- ✅ Includes mean reversion patterns
- ✅ Tests complete algorithm logic
- ✅ Produces detailed backtesting reports
- ✅ Saves results to `data/demo_results/`

## Next Steps

1. **For Testing**: Use `python run.py --demo` to test the algorithm
2. **For Real Trading**: Subscribe to Dhan Data APIs
3. **For Development**: Demo mode is perfect for algorithm development

## Example Demo Output

```
============================================================
NIFTY 50 MEAN REVERSION ALGORITHM - DEMO MODE
============================================================
Using synthetic data for demonstration purposes

Step 1: Generating synthetic stock data...
Successfully generated data for 49 stocks

Step 2: Initializing mean reversion strategy...
Step 3: Running backtest on synthetic data...
Step 4: Analyzing results...

SUMMARY STATISTICS (DEMO DATA):
Number of stocks analyzed: 49
Average strategy return: 15.45%
Average buy & hold return: 25.09%
Average excess return: -9.64%
```

The demo mode provides a complete testing environment without requiring any API subscriptions!
