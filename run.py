#!/usr/bin/env python3
"""
Launcher script for Mean Reversion Trading Algorithm
Provides easy access to different components of the system
"""

import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Mean Reversion Trading Algorithm Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Run main algorithm
  python run.py --quick-test      # Run quick test
  python run.py --demo            # Run with synthetic data (no API required)
  python run.py --live            # Run live trading system
  python run.py --backtest        # Run backtesting only
  python run.py --config          # Show configuration
  python run.py --setup           # Setup and verify installation
        """
    )
    
    parser.add_argument(
        '--quick-test',
        action='store_true',
        help='Run quick test with 5 stocks'
    )
    
    parser.add_argument(
        '--live',
        action='store_true',
        help='Run live trading system'
    )
    
    parser.add_argument(
        '--backtest',
        action='store_true',
        help='Run backtesting only'
    )
    
    parser.add_argument(
        '--config',
        action='store_true',
        help='Show current configuration'
    )
    
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Setup and verify installation'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run with demo/synthetic data (no API required)'
    )
    
    args = parser.parse_args()
    
    # Ensure we're in the right directory
    if not os.path.exists('main.py'):
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Warning: Virtual environment not detected. Consider activating it first.")
        print("Run: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)")
        print()
    
    if args.setup:
        run_setup()
    elif args.demo:
        run_demo_mode()
    elif args.config:
        show_config()
    elif args.live:
        run_live_system()
    elif args.backtest:
        run_backtest()
    elif args.quick_test:
        run_quick_test()
    else:
        run_main_algorithm()

def run_setup():
    """Setup and verify installation"""
    print("=" * 60)
    print("SETUP AND VERIFICATION")
    print("=" * 60)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check required packages
    required_packages = ['pandas', 'numpy', 'matplotlib', 'seaborn']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    # Check Dhan API
    try:
        from Dhan_Tradehull import Tradehull
        print("✓ Dhan-Tradehull")
    except ImportError:
        print("✗ Dhan-Tradehull (missing)")
        print("Install with: pip install Dhan-Tradehull")
        return False
    
    # Check configuration files
    config_files = [
        'config/config.py',
        'config/dhan_config.py',
        'config/rate_limit_config.py'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✓ {config_file}")
        else:
            print(f"✗ {config_file} (missing)")
    
    # Create necessary directories
    directories = ['logs', 'data/results', 'tests', 'docs']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    print("\nSetup completed successfully!")
    return True

def show_config():
    """Show current configuration"""
    print("=" * 60)
    print("CURRENT CONFIGURATION")
    print("=" * 60)
    
    try:
        import config.config as main_config
        print("Main Configuration:")
        print(f"  - Moving Average Period: {main_config.MOVING_AVERAGE_PERIOD}")
        print(f"  - Short Percentile: {main_config.SHORT_PERCENTILE}")
        print(f"  - Long Percentile: {main_config.LONG_PERCENTILE}")
        print(f"  - Start Date: {main_config.START_DATE}")
        print(f"  - End Date: {main_config.END_DATE}")
        print(f"  - Number of Symbols: {len(main_config.NIFTY_50_SYMBOLS)}")
    except ImportError as e:
        print(f"Error loading main config: {e}")
    
    try:
        import config.rate_limit_config as rate_config
        print("\nRate Limiting Configuration:")
        print(f"  - Rate Limit Delay: {rate_config.RATE_LIMIT_DELAY}s")
        print(f"  - Max Retries: {rate_config.MAX_RETRIES}")
        print(f"  - Max Workers: {rate_config.MAX_WORKERS}")
        print(f"  - Batch Size: {rate_config.BATCH_SIZE}")
    except ImportError as e:
        print(f"Error loading rate limit config: {e}")
    
    try:
        import config.dhan_config as dhan_cfg
        print(f"\nDhan API Configuration:")
        print(f"  - Client Code: {dhan_cfg.DHAN_CLIENT_CODE}")
        print(f"  - Token ID: {'Configured' if dhan_cfg.DHAN_CLIENT_CODE != 'your_client_code' else 'Not configured'}")
    except ImportError as e:
        print(f"Error loading Dhan config: {e}")

def run_demo_mode():
    """Run with demo/synthetic data"""
    print("=" * 60)
    print("RUNNING IN DEMO MODE")
    print("=" * 60)
    print("Using synthetic data - no API subscription required")
    print()
    
    try:
        from main import run_demo_algorithm
        success = run_demo_algorithm()
        if success:
            print("\nDemo run successful!")
        else:
            print("\nDemo run failed.")
    except Exception as e:
        print(f"Error running demo: {e}")

def run_main_algorithm():
    """Run the main algorithm"""
    print("=" * 60)
    print("RUNNING MAIN ALGORITHM")
    print("=" * 60)
    
    try:
        from main import main
        main()
    except Exception as e:
        print(f"Error running main algorithm: {e}")
        print("Try running with --setup to verify installation")

def run_quick_test():
    """Run quick test"""
    print("=" * 60)
    print("RUNNING QUICK TEST")
    print("=" * 60)
    
    try:
        from main import run_quick_test
        success = run_quick_test()
        if success:
            print("\nQuick test successful!")
        else:
            print("\nQuick test failed. Try these solutions:")
            print("1. Subscribe to Dhan Data APIs for real data")
            print("2. Run with demo data: python run.py --demo")
            print("3. Check your configuration with: python run.py --config")
    except Exception as e:
        print(f"Error running quick test: {e}")
        print("\nTry running with demo data: python run.py --demo")

def run_live_system():
    """Run live trading system"""
    print("=" * 60)
    print("RUNNING LIVE TRADING SYSTEM")
    print("=" * 60)
    
    try:
        from src.live_trading_system import main
        main()
    except Exception as e:
        print(f"Error running live system: {e}")

def run_backtest():
    """Run backtesting only"""
    print("=" * 60)
    print("RUNNING BACKTESTING")
    print("=" * 60)
    
    try:
        from main import main
        # This will run the full algorithm which includes backtesting
        main()
    except Exception as e:
        print(f"Error running backtest: {e}")

if __name__ == "__main__":
    main() 