# Rate Limiting Configuration for Dhan API
# Adjust these settings based on your API limits and requirements

# Rate Limiting Parameters
RATE_LIMIT_DELAY = 3.0  # Base delay between requests (seconds)
MAX_RETRIES = 3  # Maximum retry attempts for failed requests
BACKOFF_FACTOR = 2.0  # Exponential backoff factor
MAX_WORKERS = 3  # Maximum parallel workers (reduced for rate limiting)

# Batch Processing Settings
BATCH_SIZE = 3  # Number of symbols to process in each batch
BATCH_DELAY = 5.0  # Delay between batches (seconds)

# Error Handling
CONTINUE_ON_RATE_LIMIT = True  # Continue processing other symbols if one fails
LOG_RATE_LIMIT_ERRORS = True  # Log rate limit errors for monitoring

# Adaptive Rate Limiting
ADAPTIVE_RATE_LIMITING = True  # Automatically adjust delays based on error rate
MIN_DELAY = 1.0  # Minimum delay between requests
MAX_DELAY = 30.0  # Maximum delay between requests

# Retry Strategy
RETRY_ON_RATE_LIMIT = True  # Retry requests that hit rate limits
RETRY_ON_NETWORK_ERROR = True  # Retry on network/connection errors
RETRY_ON_TIMEOUT = True  # Retry on timeout errors

# Monitoring
TRACK_RATE_LIMIT_ERRORS = True  # Track number of rate limit errors
ALERT_ON_HIGH_ERROR_RATE = True  # Alert if error rate is too high
HIGH_ERROR_RATE_THRESHOLD = 0.3  # Alert if >30% of requests fail

# API-Specific Settings
API_TIMEOUT = 30  # API request timeout in seconds
API_MAX_REQUESTS_PER_MINUTE = 60  # Estimated API limit (adjust based on your plan)
API_MAX_REQUESTS_PER_HOUR = 1000  # Estimated hourly limit

# Fallback Strategy
USE_BATCH_PROCESSING_BY_DEFAULT = True  # Use batch processing instead of parallel
FALLBACK_TO_SEQUENTIAL = True  # Fall back to sequential processing if parallel fails
SEQUENTIAL_DELAY = 2.0  # Delay between sequential requests

# Debug Settings
DEBUG_RATE_LIMITING = False  # Enable debug output for rate limiting
LOG_ALL_REQUESTS = False  # Log all API requests (for debugging)
SHOW_RATE_LIMIT_PROGRESS = True  # Show progress during rate-limited requests 