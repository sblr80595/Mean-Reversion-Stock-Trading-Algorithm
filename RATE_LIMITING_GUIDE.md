# Rate Limiting Guide for Dhan API

This guide explains how to handle rate limiting errors when using the Dhan API with the Mean Reversion Trading Algorithm.

## Problem

The Dhan API has rate limits to prevent abuse. When you make too many requests too quickly, you'll see errors like:

```
Exception in Getting OHLC data as {'status': 'failure', 'remarks': {'error_code': 'DH-904', 'error_type': 'Rate_Limit', 'error_message': 'Too many requests on server from single user breaching rate limits. Try throttling API calls.'}, 'data': {'errorType': 'Rate_Limit', 'errorCode': 'DH-904', 'errorMessage': 'Too many requests on server from single user breaching rate limits. Try throttling API calls.'}}
```

## Solution

The improved code now includes:

### 1. Automatic Rate Limiting
- **Base delay**: 3 seconds between requests
- **Exponential backoff**: Delays increase with each retry
- **Retry logic**: Up to 3 attempts with increasing delays
- **Error detection**: Automatically detects rate limit errors

### 2. Batch Processing (Recommended)
Instead of parallel processing, use batch processing:

```python
# Use batch processing for better rate limiting
stock_data = data_loader.fetch_all_data_batch(batch_size=3)
```

### 3. Conservative Parallel Processing
If you must use parallel processing, limit workers:

```python
# Use fewer workers to avoid rate limits
data_loader = AsyncDataLoader(
    symbols=symbols,
    max_workers=3  # Limit to 3 workers
)
```

## Configuration

### Rate Limit Settings (`rate_limit_config.py`)

```python
# Rate Limiting Parameters
RATE_LIMIT_DELAY = 3.0  # Base delay between requests (seconds)
MAX_RETRIES = 3  # Maximum retry attempts
BACKOFF_FACTOR = 2.0  # Exponential backoff factor
MAX_WORKERS = 3  # Maximum parallel workers

# Batch Processing Settings
BATCH_SIZE = 3  # Number of symbols to process in each batch
BATCH_DELAY = 5.0  # Delay between batches (seconds)
```

### Adjusting Settings

**For Conservative Rate Limiting:**
```python
RATE_LIMIT_DELAY = 5.0  # 5 seconds between requests
MAX_WORKERS = 2  # Only 2 parallel workers
BATCH_SIZE = 2  # Process 2 symbols at a time
```

**For Aggressive Rate Limiting:**
```python
RATE_LIMIT_DELAY = 1.0  # 1 second between requests
MAX_WORKERS = 5  # 5 parallel workers
BATCH_SIZE = 5  # Process 5 symbols at a time
```

## Usage Examples

### 1. Basic Usage (Recommended)
```python
from data_loader_async import AsyncDataLoader

data_loader = AsyncDataLoader(
    symbols=NIFTY_50_SYMBOLS,
    start_date='2024-01-01',
    end_date='2024-12-31',
    client_code=your_client_code,
    token_id=your_token_id,
    max_workers=3  # Conservative setting
)

# Use batch processing
stock_data = data_loader.fetch_all_data_batch(batch_size=3)
```

### 2. Testing Rate Limiting
```bash
python test_rate_limiting.py
```

### 3. Monitoring Rate Limit Errors
The system tracks rate limit errors:
```python
print(f"Rate limit errors: {data_loader.rate_limit_errors}")
```

## Best Practices

### 1. Start Conservative
- Begin with 3-second delays and 2-3 workers
- Monitor error rates
- Gradually increase if no rate limits are hit

### 2. Use Batch Processing
- Batch processing is more reliable than parallel processing
- Process 2-3 symbols at a time
- Add delays between batches

### 3. Monitor and Adjust
- Track rate limit errors
- Increase delays if errors occur frequently
- Consider time-based limits (avoid peak hours)

### 4. Fallback Strategies
- If parallel processing fails, try batch processing
- If batch processing fails, try sequential processing
- Always have a fallback plan

## Error Handling

### Rate Limit Error Detection
The system automatically detects rate limit errors by looking for:
- `DH-904` error code
- `Rate_Limit` error type
- `Too many requests` message
- `breaching rate limits` message

### Retry Logic
1. **First attempt**: Normal request
2. **Rate limit hit**: Wait 6 seconds (2x base delay)
3. **Second attempt**: Wait 12 seconds (4x base delay)
4. **Third attempt**: Wait 24 seconds (8x base delay)
5. **Give up**: Log failure and continue

### Exponential Backoff
Delays increase exponentially:
- Attempt 1: 6 seconds
- Attempt 2: 12 seconds
- Attempt 3: 24 seconds

## Troubleshooting

### Still Getting Rate Limit Errors?

1. **Increase delays**:
   ```python
   RATE_LIMIT_DELAY = 5.0  # Increase to 5 seconds
   ```

2. **Reduce workers**:
   ```python
   MAX_WORKERS = 2  # Reduce to 2 workers
   ```

3. **Use smaller batches**:
   ```python
   BATCH_SIZE = 2  # Process only 2 symbols at a time
   ```

4. **Add longer delays between batches**:
   ```python
   BATCH_DELAY = 10.0  # Wait 10 seconds between batches
   ```

### Performance vs Reliability

**For Maximum Reliability:**
- Use batch processing with 2-3 symbols per batch
- 5-second delays between requests
- 10-second delays between batches
- 2 parallel workers maximum

**For Maximum Performance:**
- Use parallel processing with 3-5 workers
- 2-second delays between requests
- 5-second delays between batches
- Monitor error rates closely

## Testing

Run the test script to verify your settings:

```bash
python test_rate_limiting.py
```

This will test both batch and parallel processing with your current rate limiting settings.

## Monitoring

Track these metrics:
- **Rate limit errors**: Should be < 10% of total requests
- **Success rate**: Should be > 90%
- **Processing time**: Will increase with more conservative settings
- **Error patterns**: Look for specific symbols or times causing issues

## Advanced Configuration

### Adaptive Rate Limiting
For advanced users, you can implement adaptive rate limiting that adjusts delays based on error rates:

```python
# In rate_limit_config.py
ADAPTIVE_RATE_LIMITING = True
MIN_DELAY = 1.0
MAX_DELAY = 30.0
```

### Time-Based Limits
Consider avoiding peak trading hours:
- Market open (9:15 AM IST)
- Market close (3:30 PM IST)
- Lunch hours (12:00-1:00 PM IST)

## Summary

The improved rate limiting system provides:
- ✅ Automatic error detection and retry
- ✅ Exponential backoff for failed requests
- ✅ Configurable delays and worker limits
- ✅ Batch processing for better reliability
- ✅ Monitoring and error tracking
- ✅ Fallback strategies

Start with conservative settings and adjust based on your API plan and requirements. 