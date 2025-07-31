# Installation Guide

This guide will help you install the Mean Reversion Trading Algorithm with Dhan API integration.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Dhan trading account with API access

## Installation Options

### Option 1: Minimal Installation (Recommended)

For core functionality only:

```bash
# Upgrade pip first
pip install --upgrade pip

# Install minimal requirements
pip install -r requirements_minimal.txt
```

### Option 2: Full Installation

For all features including advanced visualizations:

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

### Option 3: Manual Installation

If you encounter conflicts, install packages manually:

```bash
# Core packages
pip install pandas>=2.1.0
pip install numpy>=1.24.4
pip install matplotlib>=3.7.0
pip install seaborn>=0.12.0
pip install requests>=2.32.3

# Dhan API
pip install Dhan-Tradehull==3.0.6

# Optional packages (for advanced features)
pip install plotly>=5.17.0
pip install dash>=2.14.2
pip install dash-bootstrap-components>=1.5.0
```

## Troubleshooting

### Common Issues

1. **Dependency Conflicts**
   ```
   ERROR: ResolutionImpossible
   ```
   **Solution**: Use minimal installation
   ```bash
   pip install -r requirements_minimal.txt
   ```

2. **Dhan-Tradehull Import Error**
   ```
   ModuleNotFoundError: No module named 'Dhan_Tradehull'
   ```
   **Solution**: Install Dhan package separately
   ```bash
   pip install Dhan-Tradehull==3.0.6
   ```

3. **Numpy Version Conflict**
   ```
   numpy version conflict
   ```
   **Solution**: Upgrade numpy
   ```bash
   pip install --upgrade numpy>=1.24.4
   ```

4. **Requests Version Conflict**
   ```
   requests version conflict
   ```
   **Solution**: Upgrade requests
   ```bash
   pip install --upgrade requests>=2.32.3
   ```

### Virtual Environment (Recommended)

Create a virtual environment to avoid conflicts:

```bash
# Create virtual environment
python -m venv trading_env

# Activate virtual environment
# On Windows:
trading_env\Scripts\activate
# On macOS/Linux:
source trading_env/bin/activate

# Install packages
pip install -r requirements_minimal.txt
```

### Testing Installation

After installation, test the setup:

```bash
# Test minimal installation
python test_minimal_install.py

# Test Dhan integration
python test_dhan_integration.py
```

## Configuration

1. **Set up Dhan credentials** in `dhan_config.py`:
   ```python
   DHAN_CLIENT_CODE = "your_client_code"
   DHAN_TOKEN_ID = "your_token_id"
   ```

2. **Test connection**:
   ```bash
   python dhan_example.py
   ```

## Usage

Once installed and configured:

```bash
# Run backtesting
python main.py

# Run live trading
python dhan_trading_system.py

# See examples
python example_usage.py
```

## Package Versions

### Minimal Requirements
- pandas >= 2.1.0
- numpy >= 1.24.4
- matplotlib >= 3.7.0
- seaborn >= 0.12.0
- requests >= 2.32.3
- Dhan-Tradehull == 3.0.6

### Full Requirements
- All minimal requirements plus:
- plotly >= 5.17.0
- dash >= 2.14.2
- dash-bootstrap-components >= 1.5.0

## Support

If you continue to have issues:

1. Check Python version: `python --version`
2. Check pip version: `pip --version`
3. Try creating a fresh virtual environment
4. Install packages one by one to identify conflicts

## Notes

- The system requires Dhan API access
- All data fetching is done through Dhan API
- No external data sources (like Yahoo Finance) are used
- The system is designed for Indian market trading 