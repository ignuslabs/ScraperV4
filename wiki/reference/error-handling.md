# Error Handling Reference

This document provides complete reference for all error codes, exceptions, and error handling patterns in ScraperV4.

## Error Handling Architecture

ScraperV4 implements a comprehensive error handling system with categorized error codes, structured exception hierarchy, and automatic error recovery mechanisms.

### Error Categories

```
System Errors (1xxx)     - Infrastructure and configuration
API Errors (2xxx)       - Web interface and endpoint errors  
Scraping Errors (3xxx)  - Scraping operation failures
Template Errors (4xxx)  - Template configuration issues
Data Errors (5xxx)      - Data storage and processing
Network Errors (6xxx)   - Network and connectivity issues
Security Errors (7xxx)  - Security and validation failures
```

## Exception Hierarchy

### Base Exceptions

#### ScraperV4Error
**Base exception for all ScraperV4 errors**

```python
class ScraperV4Error(Exception):
    """Base exception for all ScraperV4 errors."""
    
    def __init__(self, message, error_code=None, details=None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()
```

**Properties:**
- `message` (str): Human-readable error message
- `error_code` (str): Unique error identifier
- `details` (Dict): Additional error context
- `timestamp` (str): Error occurrence timestamp

### System Errors (1xxx)

#### ConfigurationError
**Error code range: 1001-1099**

Configuration and setup related errors.

```python
class ConfigurationError(ScraperV4Error):
    """Configuration or setup error."""
```

**Common Error Codes:**
- `CONFIG_001`: Invalid configuration file format
- `CONFIG_002`: Missing required configuration
- `CONFIG_003`: Invalid configuration value
- `CONFIG_004`: Configuration file not found
- `CONFIG_005`: Permission denied accessing configuration

**Example:**
```python
raise ConfigurationError(
    "Invalid timeout value in configuration",
    error_code="CONFIG_003",
    details={
        "field": "timeout",
        "value": -5,
        "expected": "positive number"
    }
)
```

#### ServiceError
**Error code range: 1101-1199**

Service initialization and dependency injection errors.

```python
class ServiceError(ScraperV4Error):
    """Service layer error."""
```

**Common Error Codes:**
- `SERVICE_001`: Service initialization failed
- `SERVICE_002`: Dependency injection error
- `SERVICE_003`: Service unavailable
- `SERVICE_004`: Service timeout
- `SERVICE_005`: Circular dependency detected

#### StorageError
**Error code range: 1201-1299**

File system and storage access errors.

```python
class StorageError(ScraperV4Error):
    """Storage operation error."""
```

**Common Error Codes:**
- `STORAGE_001`: File not found
- `STORAGE_002`: Permission denied
- `STORAGE_003`: Disk space insufficient
- `STORAGE_004`: File corruption detected
- `STORAGE_005`: Lock acquisition failed

### API Errors (2xxx)

#### APIError
**Error code range: 2001-2099**

Web API and endpoint errors.

```python
class APIError(ScraperV4Error):
    """API request error."""
```

**Common Error Codes:**
- `API_001`: Invalid request format
- `API_002`: Missing required parameter
- `API_003`: Invalid parameter value
- `API_004`: Request timeout
- `API_005`: Rate limit exceeded
- `API_006`: Authentication required
- `API_007`: Permission denied
- `API_008`: Resource not found
- `API_009`: Method not allowed
- `API_010`: Server internal error

**Response Format:**
```json
{
  "success": false,
  "error": "Missing required parameter 'template_id'",
  "error_code": "API_002",
  "details": {
    "endpoint": "/api/scraping/start",
    "method": "POST",
    "missing_parameter": "template_id",
    "received_parameters": ["job_name", "target_url"]
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Scraping Errors (3xxx)

#### ScrapingError
**Error code range: 3001-3099**

General scraping operation errors.

```python
class ScrapingError(ScraperV4Error):
    """Scraping operation error."""
```

**Common Error Codes:**
- `SCRAPING_001`: Job creation failed
- `SCRAPING_002`: Job execution failed
- `SCRAPING_003`: Job not found
- `SCRAPING_004`: Job already running
- `SCRAPING_005`: Job cancellation failed
- `SCRAPING_006`: Invalid job configuration
- `SCRAPING_007`: Maximum concurrent jobs exceeded
- `SCRAPING_008`: Job timeout exceeded
- `SCRAPING_009`: Job validation failed
- `SCRAPING_010`: Pagination limit exceeded

#### FetchError
**Error code range: 3101-3199**

Page fetching and HTTP request errors.

```python
class FetchError(ScrapingError):
    """Page fetch error."""
```

**Common Error Codes:**
- `FETCH_001`: Connection timeout
- `FETCH_002`: Connection refused
- `FETCH_003`: DNS resolution failed
- `FETCH_004`: SSL certificate error
- `FETCH_005`: Invalid response format
- `FETCH_006`: HTTP error status
- `FETCH_007`: Response too large
- `FETCH_008`: Encoding error
- `FETCH_009`: Redirect loop detected
- `FETCH_010`: Proxy connection failed

#### ExtractionError
**Error code range: 3201-3299**

Data extraction and parsing errors.

```python
class ExtractionError(ScrapingError):
    """Data extraction error."""
```

**Common Error Codes:**
- `EXTRACTION_001`: Selector not found
- `EXTRACTION_002`: Invalid selector syntax
- `EXTRACTION_003`: No data extracted
- `EXTRACTION_004`: Parsing failed
- `EXTRACTION_005`: Data type conversion failed
- `EXTRACTION_006`: Required field missing
- `EXTRACTION_007`: Extraction timeout
- `EXTRACTION_008`: Invalid HTML structure
- `EXTRACTION_009`: JavaScript execution failed
- `EXTRACTION_010`: Anti-bot protection detected

#### StealthError
**Error code range: 3301-3399**

Stealth mode and anti-detection errors.

```python
class StealthError(ScrapingError):
    """Stealth operation error."""
```

**Common Error Codes:**
- `STEALTH_001`: Browser launch failed
- `STEALTH_002`: Stealth detection bypassed
- `STEALTH_003`: CAPTCHA encountered
- `STEALTH_004`: Challenge solving failed
- `STEALTH_005`: Fingerprint detection
- `STEALTH_006`: Behavior analysis triggered
- `STEALTH_007`: IP address blocked
- `STEALTH_008`: User agent blocked
- `STEALTH_009`: Rate limiting detected
- `STEALTH_010`: Session terminated

### Template Errors (4xxx)

#### TemplateError
**Error code range: 4001-4099**

Template configuration and validation errors.

```python
class TemplateError(ScraperV4Error):
    """Template configuration error."""
```

**Common Error Codes:**
- `TEMPLATE_001`: Template not found
- `TEMPLATE_002`: Invalid template format
- `TEMPLATE_003`: Template validation failed
- `TEMPLATE_004`: Selector configuration invalid
- `TEMPLATE_005`: Fetcher configuration invalid
- `TEMPLATE_006`: Template already exists
- `TEMPLATE_007`: Template in use, cannot delete
- `TEMPLATE_008`: Template version mismatch
- `TEMPLATE_009`: Required template field missing
- `TEMPLATE_010`: Template circular dependency

#### ValidationError
**Error code range: 4101-4199**

Data validation and rule errors.

```python
class ValidationError(TemplateError):
    """Data validation error."""
```

**Common Error Codes:**
- `VALIDATION_001`: Required field validation failed
- `VALIDATION_002`: Data type validation failed
- `VALIDATION_003`: Pattern validation failed
- `VALIDATION_004`: Range validation failed
- `VALIDATION_005`: Custom validation failed
- `VALIDATION_006`: Validation rule syntax error
- `VALIDATION_007`: Cross-field validation failed
- `VALIDATION_008`: Validation timeout
- `VALIDATION_009`: Validation rule not found
- `VALIDATION_010`: Validation circular reference

### Data Errors (5xxx)

#### DataError
**Error code range: 5001-5099**

Data processing and storage errors.

```python
class DataError(ScraperV4Error):
    """Data operation error."""
```

**Common Error Codes:**
- `DATA_001`: Data save failed
- `DATA_002`: Data load failed
- `DATA_003`: Data corruption detected
- `DATA_004`: Data format invalid
- `DATA_005`: Data size limit exceeded
- `DATA_006`: Data encoding error
- `DATA_007`: Data transformation failed
- `DATA_008`: Data export failed
- `DATA_009`: Data import failed
- `DATA_010`: Data cleanup failed

#### ExportError
**Error code range: 5101-5199**

Data export and file generation errors.

```python
class ExportError(DataError):
    """Data export error."""
```

**Common Error Codes:**
- `EXPORT_001`: Export format not supported
- `EXPORT_002`: Export file creation failed
- `EXPORT_003`: Export data preparation failed
- `EXPORT_004`: Export permission denied
- `EXPORT_005`: Export disk space insufficient
- `EXPORT_006`: Export template invalid
- `EXPORT_007`: Export compression failed
- `EXPORT_008`: Export streaming failed
- `EXPORT_009`: Export timeout exceeded
- `EXPORT_010`: Export validation failed

### Network Errors (6xxx)

#### NetworkError
**Error code range: 6001-6099**

Network connectivity and communication errors.

```python
class NetworkError(ScraperV4Error):
    """Network operation error."""
```

**Common Error Codes:**
- `NETWORK_001`: Connection timeout
- `NETWORK_002`: Connection refused
- `NETWORK_003`: Network unreachable
- `NETWORK_004`: DNS resolution failed
- `NETWORK_005`: SSL handshake failed
- `NETWORK_006`: Certificate verification failed
- `NETWORK_007`: Proxy authentication failed
- `NETWORK_008`: Proxy connection failed
- `NETWORK_009`: Protocol error
- `NETWORK_010`: Network interface error

#### ProxyError
**Error code range: 6101-6199**

Proxy configuration and connection errors.

```python
class ProxyError(NetworkError):
    """Proxy operation error."""
```

**Common Error Codes:**
- `PROXY_001`: Proxy configuration invalid
- `PROXY_002`: Proxy connection failed
- `PROXY_003`: Proxy authentication failed
- `PROXY_004`: Proxy timeout
- `PROXY_005`: Proxy not responding
- `PROXY_006`: Proxy IP blocked
- `PROXY_007`: Proxy rate limited
- `PROXY_008`: Proxy SSL error
- `PROXY_009`: Proxy protocol mismatch
- `PROXY_010`: Proxy pool exhausted

### Security Errors (7xxx)

#### SecurityError
**Error code range: 7001-7099**

Security validation and protection errors.

```python
class SecurityError(ScraperV4Error):
    """Security validation error."""
```

**Common Error Codes:**
- `SECURITY_001`: URL validation failed
- `SECURITY_002`: Suspicious pattern detected
- `SECURITY_003`: Private IP access blocked
- `SECURITY_004`: Localhost access blocked
- `SECURITY_005`: Dangerous port blocked
- `SECURITY_006`: Malicious content detected
- `SECURITY_007`: SSRF attempt blocked
- `SECURITY_008`: Path traversal blocked
- `SECURITY_009`: Script injection blocked
- `SECURITY_010`: Authentication required

#### AuthenticationError
**Error code range: 7101-7199**

Authentication and authorization errors.

```python
class AuthenticationError(SecurityError):
    """Authentication error."""
```

**Common Error Codes:**
- `AUTH_001`: Invalid credentials
- `AUTH_002`: Token expired
- `AUTH_003`: Token invalid
- `AUTH_004`: Permission denied
- `AUTH_005`: Account suspended
- `AUTH_006`: Rate limit exceeded
- `AUTH_007`: IP address blocked
- `AUTH_008`: Session expired
- `AUTH_009`: Two-factor authentication required
- `AUTH_010`: Account locked

## Error Response Formats

### Standard API Error Response

```json
{
  "success": false,
  "error": "Human-readable error message",
  "error_code": "ERROR_CODE_001",
  "details": {
    "context_field1": "context_value1",
    "context_field2": "context_value2",
    "suggestions": ["Try this", "Or this"]
  },
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "req_123456789"
}
```

### Validation Error Response

```json
{
  "success": false,
  "error": "Validation failed",
  "error_code": "VALIDATION_001",
  "validation_errors": [
    {
      "field": "email",
      "error": "Invalid email format",
      "value": "invalid-email",
      "expected": "valid email address"
    },
    {
      "field": "age",
      "error": "Value out of range",
      "value": -5,
      "expected": "0-120"
    }
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Scraping Error Response

```json
{
  "success": false,
  "error": "Failed to extract data from page",
  "error_code": "EXTRACTION_001",
  "details": {
    "url": "https://example.com/page",
    "template": "product_scraper",
    "failed_selectors": [
      {
        "field": "price",
        "selector": ".price-current",
        "error": "Selector not found"
      }
    ],
    "suggestions": [
      "Check if page structure changed",
      "Update template selectors",
      "Try fallback selectors"
    ]
  },
  "recovery_actions": [
    "retry_with_fallback",
    "manual_selector_update"
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Error Handling Patterns

### Try-Catch with Specific Handling

```python
from src.exceptions import ScrapingError, FetchError, ExtractionError

try:
    result = scraper.scrape(url)
except FetchError as e:
    if e.error_code == "FETCH_001":  # Timeout
        logger.warning(f"Timeout fetching {url}, retrying with longer timeout")
        # Retry with increased timeout
    elif e.error_code == "FETCH_003":  # DNS error
        logger.error(f"DNS resolution failed for {url}")
        # Skip URL or use alternative
    else:
        # Generic fetch error handling
        logger.error(f"Fetch error: {e}")
        
except ExtractionError as e:
    if e.error_code == "EXTRACTION_001":  # Selector not found
        logger.warning(f"Selector failed, trying fallback selectors")
        # Try alternative selectors
    else:
        # Generic extraction error
        logger.error(f"Extraction error: {e}")
        
except ScrapingError as e:
    # Catch-all for other scraping errors
    logger.error(f"Scraping failed: {e}")
    
except Exception as e:
    # Unexpected error
    logger.critical(f"Unexpected error: {e}")
    raise
```

### Automatic Error Recovery

```python
from src.utils.retry import retry_with_backoff
from src.exceptions import NetworkError, FetchError

@retry_with_backoff(
    max_attempts=3,
    backoff_factor=2,
    exceptions=(NetworkError, FetchError)
)
def fetch_with_retry(url):
    try:
        return fetcher.fetch(url)
    except FetchError as e:
        if e.error_code in ["FETCH_001", "FETCH_002"]:  # Retryable errors
            logger.info(f"Retryable error: {e.error_code}, will retry")
            raise  # Let retry decorator handle it
        else:
            logger.error(f"Non-retryable error: {e.error_code}")
            raise  # Don't retry
```

### Error Aggregation

```python
from src.exceptions import ValidationError

def validate_template(template_data):
    errors = []
    
    try:
        validate_selectors(template_data.get('selectors', {}))
    except ValidationError as e:
        errors.append(e)
    
    try:
        validate_fetcher_config(template_data.get('fetcher_config', {}))
    except ValidationError as e:
        errors.append(e)
    
    if errors:
        raise ValidationError(
            f"Template validation failed with {len(errors)} errors",
            error_code="VALIDATION_001",
            details={
                "error_count": len(errors),
                "errors": [
                    {
                        "error_code": e.error_code,
                        "message": str(e),
                        "details": e.details
                    }
                    for e in errors
                ]
            }
        )
```

## Error Recovery Strategies

### Automatic Recovery

#### Retry with Exponential Backoff
```python
def retry_with_exponential_backoff(func, max_attempts=3, base_delay=1):
    for attempt in range(max_attempts):
        try:
            return func()
        except (NetworkError, FetchError) as e:
            if attempt == max_attempts - 1:
                raise
            
            delay = base_delay * (2 ** attempt)
            logger.info(f"Attempt {attempt + 1} failed, retrying in {delay}s")
            time.sleep(delay)
```

#### Fallback Strategies
```python
def scrape_with_fallback(url, primary_fetcher, fallback_fetchers):
    fetchers = [primary_fetcher] + fallback_fetchers
    
    for i, fetcher in enumerate(fetchers):
        try:
            return fetcher.fetch(url)
        except FetchError as e:
            if i == len(fetchers) - 1:  # Last fetcher
                raise
            
            logger.warning(f"Fetcher {i} failed ({e.error_code}), trying next")
            continue
```

#### Circuit Breaker Pattern
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time < self.timeout:
                raise CircuitBreakerError("Circuit breaker is open")
            else:
                self.state = "half-open"
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failure_count = 0
        self.state = "closed"
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
```

### Manual Recovery

#### Error Analysis and Reporting
```python
def analyze_scraping_errors(job_id):
    errors = get_job_errors(job_id)
    
    error_analysis = {
        "total_errors": len(errors),
        "error_types": {},
        "most_common_errors": [],
        "recommendations": []
    }
    
    # Categorize errors
    for error in errors:
        error_type = error["error_code"][:error["error_code"].find("_")]
        error_analysis["error_types"][error_type] = (
            error_analysis["error_types"].get(error_type, 0) + 1
        )
    
    # Generate recommendations
    if error_analysis["error_types"].get("FETCH", 0) > 5:
        error_analysis["recommendations"].append(
            "High number of fetch errors - consider adjusting timeouts or using proxies"
        )
    
    if error_analysis["error_types"].get("EXTRACTION", 0) > 3:
        error_analysis["recommendations"].append(
            "Multiple extraction errors - template selectors may need updating"
        )
    
    return error_analysis
```

## Error Monitoring and Alerts

### Error Metrics Collection

```python
from src.utils.metrics import ErrorMetrics

class ErrorTracker:
    def __init__(self):
        self.metrics = ErrorMetrics()
    
    def record_error(self, error):
        self.metrics.increment_counter(
            "errors_total",
            labels={
                "error_code": error.error_code,
                "error_type": error.__class__.__name__,
                "component": self._get_component_from_stack()
            }
        )
        
        self.metrics.observe_histogram(
            "error_resolution_time",
            time.time() - error.timestamp
        )
    
    def get_error_rate(self, time_window="1h"):
        return self.metrics.get_rate("errors_total", time_window)
    
    def get_top_errors(self, limit=10):
        return self.metrics.get_top_series("errors_total", limit)
```

### Alert Configuration

```python
def setup_error_alerts():
    alerts = [
        {
            "name": "high_error_rate",
            "condition": "error_rate > 0.1",  # 10% error rate
            "window": "5m",
            "severity": "warning",
            "action": "notify_team"
        },
        {
            "name": "critical_errors",
            "condition": "critical_errors > 0",
            "window": "1m",
            "severity": "critical",
            "action": "page_oncall"
        },
        {
            "name": "service_down",
            "condition": "service_availability < 0.95",
            "window": "2m",
            "severity": "critical",
            "action": "emergency_escalation"
        }
    ]
    
    for alert in alerts:
        register_alert(alert)
```

## Debugging and Troubleshooting

### Error Context Collection

```python
def collect_error_context(error, request_context=None):
    context = {
        "error": {
            "type": error.__class__.__name__,
            "message": str(error),
            "code": getattr(error, 'error_code', None),
            "details": getattr(error, 'details', {}),
            "timestamp": getattr(error, 'timestamp', None)
        },
        "stack_trace": traceback.format_exc(),
        "system": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "memory_usage": psutil.virtual_memory()._asdict(),
            "disk_usage": psutil.disk_usage('/')._asdict()
        },
        "application": {
            "version": config.version,
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "active_jobs": get_active_job_count(),
            "uptime": get_application_uptime()
        }
    }
    
    if request_context:
        context["request"] = request_context
    
    return context
```

### Error Reproduction

```python
def create_error_reproduction_case(error_context):
    """Create a test case that can reproduce the error."""
    
    reproduction_case = {
        "test_name": f"reproduce_{error_context['error']['code']}",
        "setup": {
            "configuration": get_current_config(),
            "templates": get_relevant_templates(error_context),
            "test_data": extract_test_data(error_context)
        },
        "steps": generate_reproduction_steps(error_context),
        "expected_error": {
            "type": error_context["error"]["type"],
            "code": error_context["error"]["code"],
            "message_pattern": extract_message_pattern(
                error_context["error"]["message"]
            )
        }
    }
    
    return reproduction_case
```

## Best Practices

### Error Prevention

1. **Input Validation**: Validate all inputs at API boundaries
2. **Configuration Validation**: Validate configuration on startup
3. **Resource Limits**: Set appropriate timeouts and limits
4. **Graceful Degradation**: Provide fallback options
5. **Health Checks**: Implement comprehensive health monitoring

### Error Handling

1. **Specific Exceptions**: Catch specific exceptions, not generic ones
2. **Error Context**: Include relevant context in error messages
3. **Error Codes**: Use consistent error coding schemes
4. **Logging**: Log errors with appropriate severity levels
5. **User-Friendly Messages**: Provide actionable error messages

### Error Recovery

1. **Retry Logic**: Implement intelligent retry strategies
2. **Circuit Breakers**: Prevent cascade failures
3. **Fallback Mechanisms**: Provide alternative execution paths
4. **Cleanup**: Ensure proper resource cleanup on errors
5. **State Recovery**: Design for state recovery after failures

## See Also

- [API Endpoints](api/) - API error responses and codes
- [Configuration Reference](configuration/) - Configuration error handling
- [Services Reference](classes/services.md) - Service error handling
- [Utilities Reference](classes/utilities.md) - Error handling utilities