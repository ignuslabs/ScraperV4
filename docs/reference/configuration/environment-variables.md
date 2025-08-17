# Environment Variables Reference

This document provides complete reference for all environment variables and configuration options in ScraperV4.

## Core Application Settings

### Basic Configuration

**APP_NAME** *(optional)*
- **Default:** `ScraperV4`
- **Description:** Application name used in logs and UI
- **Example:** `APP_NAME=MyCustomScraper`

**APP_VERSION** *(optional)*
- **Default:** `1.0.0`
- **Description:** Application version string
- **Example:** `APP_VERSION=2.1.0`

**DEBUG** *(optional)*
- **Default:** `False`
- **Type:** Boolean
- **Description:** Enable debug mode with verbose logging
- **Example:** `DEBUG=True`

### Storage Configuration

**DATA_FOLDER** *(optional)*
- **Default:** `data`
- **Description:** Root directory for all data storage
- **Example:** `DATA_FOLDER=/var/scraperv4/data`

**JOBS_FOLDER** *(optional)*
- **Default:** `data/jobs`
- **Description:** Directory for job metadata storage
- **Example:** `JOBS_FOLDER=/var/scraperv4/jobs`

**RESULTS_FOLDER** *(optional)*
- **Default:** `data/results`
- **Description:** Directory for scraped results storage
- **Example:** `RESULTS_FOLDER=/var/scraperv4/results`

**TEMPLATES_FOLDER** *(optional)*
- **Default:** `templates`
- **Description:** Directory for template files
- **Example:** `TEMPLATES_FOLDER=/etc/scraperv4/templates`

## Scraping Configuration

### Basic Scraping Settings

**DEFAULT_DELAY** *(optional)*
- **Default:** `2.0`
- **Type:** Float
- **Range:** 0.1 - 60.0
- **Unit:** Seconds
- **Description:** Default delay between HTTP requests
- **Example:** `DEFAULT_DELAY=1.5`

**MAX_RETRIES** *(optional)*
- **Default:** `3`
- **Type:** Integer
- **Range:** 0 - 10
- **Description:** Maximum retry attempts for failed requests
- **Example:** `MAX_RETRIES=5`

**REQUEST_TIMEOUT** *(optional)*
- **Default:** `30`
- **Type:** Integer
- **Range:** 5 - 300
- **Unit:** Seconds
- **Description:** HTTP request timeout duration
- **Example:** `REQUEST_TIMEOUT=60`

**STEALTH_MODE** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Enable stealth browsing features
- **Example:** `STEALTH_MODE=False`

**CONCURRENT_JOBS** *(optional)*
- **Default:** `3`
- **Type:** Integer
- **Range:** 1 - 10
- **Description:** Maximum number of simultaneous scraping jobs
- **Example:** `CONCURRENT_JOBS=5`

**USER_AGENT** *(optional)*
- **Default:** `ScraperV4/1.0`
- **Description:** Default User-Agent header for requests
- **Example:** `USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36`

### Advanced Scraping Settings

**RATE_LIMIT_REQUESTS** *(optional)*
- **Default:** `100`
- **Type:** Integer
- **Description:** Maximum requests per minute
- **Example:** `RATE_LIMIT_REQUESTS=50`

**RATE_LIMIT_WINDOW** *(optional)*
- **Default:** `60`
- **Type:** Integer
- **Unit:** Seconds
- **Description:** Rate limiting time window
- **Example:** `RATE_LIMIT_WINDOW=120`

**FOLLOW_REDIRECTS** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Automatically follow HTTP redirects
- **Example:** `FOLLOW_REDIRECTS=False`

**MAX_REDIRECTS** *(optional)*
- **Default:** `5`
- **Type:** Integer
- **Range:** 0 - 20
- **Description:** Maximum number of redirects to follow
- **Example:** `MAX_REDIRECTS=3`

## Scrapling Fetcher Configuration

### Basic Scrapling Settings

**SCRAPLING_STEALTH_MODE** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Enable Scrapling stealth features
- **Example:** `SCRAPLING_STEALTH_MODE=False`

**SCRAPLING_USER_AGENT** *(optional)*
- **Default:** `ScraperV4/1.0`
- **Description:** User-Agent for Scrapling requests
- **Example:** `SCRAPLING_USER_AGENT=CustomBot/2.0`

**SCRAPLING_TIMEOUT** *(optional)*
- **Default:** `30`
- **Type:** Integer
- **Range:** 5 - 300
- **Unit:** Seconds
- **Description:** Scrapling request timeout
- **Example:** `SCRAPLING_TIMEOUT=45`

**SCRAPLING_MAX_RETRIES** *(optional)*
- **Default:** `3`
- **Type:** Integer
- **Range:** 0 - 10
- **Description:** Maximum retry attempts for Scrapling
- **Example:** `SCRAPLING_MAX_RETRIES=2`

**SCRAPLING_DELAY_MIN** *(optional)*
- **Default:** `1`
- **Type:** Integer
- **Unit:** Seconds
- **Description:** Minimum delay between Scrapling requests
- **Example:** `SCRAPLING_DELAY_MIN=2`

**SCRAPLING_DELAY_MAX** *(optional)*
- **Default:** `3`
- **Type:** Integer
- **Unit:** Seconds
- **Description:** Maximum delay between Scrapling requests
- **Example:** `SCRAPLING_DELAY_MAX=5`

### Stealth Configuration

**BLOCK_WEBRTC** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Block WebRTC to prevent IP leaks
- **Example:** `BLOCK_WEBRTC=False`

**SPOOF_CANVAS** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Spoof canvas fingerprinting
- **Example:** `SPOOF_CANVAS=False`

**OS_RANDOMIZATION** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Randomize OS fingerprints
- **Example:** `OS_RANDOMIZATION=False`

**GOOGLE_SEARCH_SIMULATION** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Simulate coming from Google search
- **Example:** `GOOGLE_SEARCH_SIMULATION=False`

**DISABLE_ADS** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Block advertisement requests
- **Example:** `DISABLE_ADS=False`

## Web Interface Configuration

### Eel Server Settings

**EEL_PORT** *(optional)*
- **Default:** `8080`
- **Type:** Integer
- **Range:** 1024 - 65535
- **Description:** Port for Eel web interface
- **Example:** `EEL_PORT=3000`

**EEL_DEBUG** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Enable Eel debug mode
- **Example:** `EEL_DEBUG=False`

**WEB_FOLDER** *(optional)*
- **Default:** `web`
- **Description:** Directory containing web interface files
- **Example:** `WEB_FOLDER=/var/www/scraperv4`

**ALLOWED_EXTENSIONS** *(optional)*
- **Default:** `.html,.css,.js,.png,.jpg,.gif`
- **Description:** Comma-separated list of allowed file extensions
- **Example:** `ALLOWED_EXTENSIONS=.html,.css,.js,.svg,.ico`

### Security Settings

**CORS_ORIGINS** *(optional)*
- **Default:** `*`
- **Description:** Allowed CORS origins (comma-separated)
- **Example:** `CORS_ORIGINS=http://localhost:3000,https://myapp.com`

**API_KEY** *(optional)*
- **Default:** None
- **Description:** Optional API key for authentication
- **Example:** `API_KEY=your-secret-api-key-here`

**ENABLE_AUTHENTICATION** *(optional)*
- **Default:** `False`
- **Type:** Boolean
- **Description:** Enable API authentication
- **Example:** `ENABLE_AUTHENTICATION=True`

## Logging Configuration

### Log Levels and Output

**LOG_LEVEL** *(optional)*
- **Default:** `INFO`
- **Options:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Description:** Minimum log level to record
- **Example:** `LOG_LEVEL=DEBUG`

**LOG_FILE** *(optional)*
- **Default:** `logs/scraperv4.log`
- **Description:** Path to main log file
- **Example:** `LOG_FILE=/var/log/scraperv4/app.log`

**LOG_MAX_BYTES** *(optional)*
- **Default:** `10000000` (10MB)
- **Type:** Integer
- **Description:** Maximum log file size before rotation
- **Example:** `LOG_MAX_BYTES=50000000`

**LOG_BACKUP_COUNT** *(optional)*
- **Default:** `5`
- **Type:** Integer
- **Description:** Number of rotated log files to keep
- **Example:** `LOG_BACKUP_COUNT=10`

**LOG_FORMAT** *(optional)*
- **Default:** `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Description:** Python logging format string
- **Example:** `LOG_FORMAT=[%(levelname)s] %(asctime)s: %(message)s`

### Specialized Logging

**ENABLE_FRONTEND_LOGGING** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Enable frontend activity logging
- **Example:** `ENABLE_FRONTEND_LOGGING=False`

**FRONTEND_LOG_FILE** *(optional)*
- **Default:** `logs/frontend.log`
- **Description:** Path to frontend log file
- **Example:** `FRONTEND_LOG_FILE=/var/log/scraperv4/frontend.log`

**PERFORMANCE_LOGGING** *(optional)*
- **Default:** `False`
- **Type:** Boolean
- **Description:** Enable detailed performance logging
- **Example:** `PERFORMANCE_LOGGING=True`

**ERROR_TRACKING** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Enable error tracking and reporting
- **Example:** `ERROR_TRACKING=False`

## Database Configuration

### Storage Backend

**DATABASE_TYPE** *(optional)*
- **Default:** `file`
- **Options:** `file`, `sqlite`, `memory`
- **Description:** Storage backend type
- **Example:** `DATABASE_TYPE=sqlite`

**DATABASE_PATH** *(optional)*
- **Default:** `data/scraperv4.db`
- **Description:** Database file path (for file/sqlite backends)
- **Example:** `DATABASE_PATH=/var/lib/scraperv4/data.db`

**DATABASE_URL** *(optional)*
- **Default:** None
- **Description:** Full database connection URL
- **Example:** `DATABASE_URL=sqlite:///var/lib/scraperv4/data.db`

### Performance Settings

**CONNECTION_POOL_SIZE** *(optional)*
- **Default:** `10`
- **Type:** Integer
- **Description:** Database connection pool size
- **Example:** `CONNECTION_POOL_SIZE=20`

**QUERY_TIMEOUT** *(optional)*
- **Default:** `30`
- **Type:** Integer
- **Unit:** Seconds
- **Description:** Database query timeout
- **Example:** `QUERY_TIMEOUT=60`

## Performance and Optimization

### Memory Management

**MAX_MEMORY_USAGE** *(optional)*
- **Default:** `1024` (1GB)
- **Type:** Integer
- **Unit:** MB
- **Description:** Maximum memory usage before cleanup
- **Example:** `MAX_MEMORY_USAGE=2048`

**GARBAGE_COLLECTION_INTERVAL** *(optional)*
- **Default:** `300` (5 minutes)
- **Type:** Integer
- **Unit:** Seconds
- **Description:** Automatic garbage collection interval
- **Example:** `GARBAGE_COLLECTION_INTERVAL=600`

### Caching

**ENABLE_TEMPLATE_CACHE** *(optional)*
- **Default:** `True`
- **Type:** Boolean
- **Description:** Enable template caching in memory
- **Example:** `ENABLE_TEMPLATE_CACHE=False`

**TEMPLATE_CACHE_SIZE** *(optional)*
- **Default:** `100`
- **Type:** Integer
- **Description:** Maximum templates to cache
- **Example:** `TEMPLATE_CACHE_SIZE=200`

**CACHE_TTL** *(optional)*
- **Default:** `3600` (1 hour)
- **Type:** Integer
- **Unit:** Seconds
- **Description:** Cache time-to-live
- **Example:** `CACHE_TTL=7200`

## Development and Testing

### Development Mode

**DEVELOPMENT_MODE** *(optional)*
- **Default:** `False`
- **Type:** Boolean
- **Description:** Enable development features
- **Example:** `DEVELOPMENT_MODE=True`

**HOT_RELOAD** *(optional)*
- **Default:** `False`
- **Type:** Boolean
- **Description:** Enable hot reloading (development only)
- **Example:** `HOT_RELOAD=True`

**MOCK_REQUESTS** *(optional)*
- **Default:** `False`
- **Type:** Boolean
- **Description:** Use mock HTTP responses for testing
- **Example:** `MOCK_REQUESTS=True`

### Testing Configuration

**TEST_MODE** *(optional)*
- **Default:** `False`
- **Type:** Boolean
- **Description:** Enable test mode with isolated storage
- **Example:** `TEST_MODE=True`

**TEST_DATA_PATH** *(optional)*
- **Default:** `tests/data`
- **Description:** Path to test data files
- **Example:** `TEST_DATA_PATH=/tmp/scraperv4-tests`

## Configuration File Example

Create a `.env` file in the project root with your configuration:

```bash
# Basic Application Settings
APP_NAME=MyScraperV4
DEBUG=False

# Storage Configuration
DATA_FOLDER=/var/scraperv4/data
TEMPLATES_FOLDER=/etc/scraperv4/templates

# Scraping Settings
DEFAULT_DELAY=1.5
MAX_RETRIES=5
REQUEST_TIMEOUT=60
STEALTH_MODE=True
CONCURRENT_JOBS=5

# Scrapling Configuration
SCRAPLING_STEALTH_MODE=True
SCRAPLING_TIMEOUT=45
SCRAPLING_DELAY_MIN=2
SCRAPLING_DELAY_MAX=5

# Web Interface
EEL_PORT=3000
EEL_DEBUG=False

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/scraperv4/app.log
LOG_MAX_BYTES=50000000
LOG_BACKUP_COUNT=10

# Performance
MAX_MEMORY_USAGE=2048
ENABLE_TEMPLATE_CACHE=True
TEMPLATE_CACHE_SIZE=200
```

## Configuration Validation

ScraperV4 automatically validates configuration values on startup:

### Validation Rules
- Numeric values must be within specified ranges
- Boolean values accept: `True`, `False`, `1`, `0`, `yes`, `no`
- File paths are checked for accessibility
- Port numbers are validated for availability
- Dependencies are checked for required features

### Invalid Configuration Handling
- **Warning:** Non-critical invalid values fall back to defaults
- **Error:** Critical invalid values prevent startup
- **Logging:** All validation issues are logged at startup

## Configuration Priority

Configuration values are loaded in the following priority order (highest to lowest):

1. **Environment Variables** - Direct environment variable values
2. **`.env` File** - Values from `.env` file in project root
3. **Configuration File** - Values from explicit config file
4. **Command Line Arguments** - Runtime arguments (if supported)
5. **Default Values** - Built-in default values

## See Also

- [Template Schema](template-schema.md) - Template configuration reference
- [Proxy Settings](proxy-settings.md) - Proxy configuration options
- [Stealth Options](stealth-options.md) - Anti-detection configuration
- [Services Reference](../classes/services.md) - Service configuration options