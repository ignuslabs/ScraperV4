# Utilities Reference

This document provides complete reference for all utility functions and helper classes in ScraperV4, which provide common functionality across the application.

## Utility Modules Overview

ScraperV4 includes several utility modules providing cross-cutting concerns:

```
src/utils/
├── validation_utils.py    # URL and data validation
├── data_utils.py         # Data processing and transformation
├── logging_utils.py      # Logging configuration and helpers
└── __init__.py          # Module initialization
```

## Validation Utilities

**File:** `src/utils/validation_utils.py`

Provides comprehensive validation functions for URLs, selectors, and configuration data.

### URL Validation

#### `validate_url(url)`
Validates URL format and basic accessibility.

**Parameters:**
- `url` (str): URL to validate

**Returns:** `Dict[str, Any]` with validation results

**Response Format:**
```python
{
    "valid": True,
    "url": "https://example.com/page",
    "domain": "example.com",
    "scheme": "https",
    "path": "/page",
    "query": "param=value",
    "fragment": "section"
}

# For invalid URLs:
{
    "valid": False,
    "error": "URL must start with http:// or https://"
}
```

**Validation Checks:**
- Non-empty string validation
- Protocol validation (HTTP/HTTPS only)
- Domain name validation
- URL structure parsing
- Basic format verification

**Example:**
```python
from src.utils.validation_utils import validate_url

result = validate_url("https://example.com/products")
if result["valid"]:
    print(f"Valid URL: {result['domain']}")
else:
    print(f"Invalid URL: {result['error']}")
```

### Selector Validation

#### `validate_selector(selector, selector_type="css")`
Validates CSS or XPath selector syntax.

**Parameters:**
- `selector` (str): Selector string to validate
- `selector_type` (str): Type of selector ("css" or "xpath")

**Returns:** `Dict[str, Any]` with validation results

**Response Format:**
```python
{
    "valid": True,
    "selector": "h1.title",
    "type": "css",
    "specificity": 11,
    "warnings": []
}

# For invalid selectors:
{
    "valid": False,
    "error": "Invalid CSS selector syntax",
    "suggestions": ["Try 'h1.title' instead"]
}
```

**CSS Selector Validation:**
- Syntax validation using CSS parser
- Specificity calculation
- Common error detection
- Best practice suggestions

**XPath Selector Validation:**
- XPath syntax validation
- Axis and function validation
- Performance warnings for complex paths

**Example:**
```python
from src.utils.validation_utils import validate_selector

# CSS selector validation
css_result = validate_selector("h1.product-title")

# XPath selector validation
xpath_result = validate_selector("//h1[@class='title']", "xpath")
```

### Configuration Validation

#### `validate_scraping_config(config)`
Validates scraping configuration parameters.

**Parameters:**
- `config` (Dict[str, Any]): Configuration dictionary

**Returns:** `Dict[str, Any]` with validation results

**Response Format:**
```python
{
    "valid": True,
    "errors": [],
    "warnings": [
        "High timeout value may cause slow performance"
    ],
    "suggestions": [
        "Consider reducing concurrent_requests for better stability"
    ]
}
```

**Validated Parameters:**
- `timeout`: Request timeout (positive number)
- `max_retries`: Retry attempts (non-negative integer)
- `delay_range`: Delay range tuple (min < max)
- `user_agent`: User-Agent string format
- `concurrent_requests`: Concurrency limit
- `proxy_config`: Proxy configuration
- `headers`: HTTP headers format

**Example:**
```python
from src.utils.validation_utils import validate_scraping_config

config = {
    "timeout": 30,
    "max_retries": 3,
    "delay_range": [1, 5],
    "concurrent_requests": 5
}

result = validate_scraping_config(config)
if result["valid"]:
    print("Configuration is valid")
else:
    print(f"Errors: {result['errors']}")
```

#### `test_selector(url, selector)`
Tests selector against a live URL to check if it finds elements.

**Parameters:**
- `url` (str): URL to test against
- `selector` (str): CSS selector to test

**Returns:** `Dict[str, Any]` with test results

**Response Format:**
```python
{
    "matches": True,
    "count": 5,
    "sample_data": [
        "First matching element text",
        "Second matching element text",
        "Third matching element text"
    ],
    "selector": "h2.product-title",
    "url": "https://example.com",
    "response_time": 1.2
}
```

**Example:**
```python
from src.utils.validation_utils import test_selector

result = test_selector(
    "https://example.com/products",
    ".product-title"
)

if result["matches"]:
    print(f"Found {result['count']} matches")
else:
    print("No matches found")
```

## Data Utilities

**File:** `src/utils/data_utils.py`

Provides data processing, transformation, and export utilities.

### Data Processing

#### `clean_text(text, options=None)`
Cleans and normalizes text data.

**Parameters:**
- `text` (str): Text to clean
- `options` (Dict[str, Any], optional): Cleaning options

**Options:**
- `strip_whitespace`: Remove leading/trailing whitespace (default: True)
- `normalize_spaces`: Convert multiple spaces to single space (default: True)
- `remove_html`: Strip HTML tags (default: False)
- `decode_entities`: Decode HTML entities (default: True)
- `fix_encoding`: Fix common encoding issues (default: True)

**Returns:** `str` - Cleaned text

**Example:**
```python
from src.utils.data_utils import clean_text

dirty_text = "  Product &amp; Title  \n\n  "
clean = clean_text(dirty_text, {
    "strip_whitespace": True,
    "normalize_spaces": True,
    "decode_entities": True
})
# Result: "Product & Title"
```

#### `extract_numbers(text, return_type="float")`
Extracts numeric values from text.

**Parameters:**
- `text` (str): Text containing numbers
- `return_type` (str): Type to return ("float", "int", "all")

**Returns:** Numeric value(s) or None

**Example:**
```python
from src.utils.data_utils import extract_numbers

price_text = "Price: $29.99 (was $39.99)"
price = extract_numbers(price_text, "float")
# Result: 29.99

all_prices = extract_numbers(price_text, "all")
# Result: [29.99, 39.99]
```

#### `normalize_url(url, base_url=None)`
Normalizes and resolves URLs.

**Parameters:**
- `url` (str): URL to normalize
- `base_url` (str, optional): Base URL for relative URLs

**Returns:** `str` - Normalized absolute URL

**Features:**
- Converts relative URLs to absolute
- Removes URL fragments
- Normalizes query parameters
- Handles redirects and canonical URLs

**Example:**
```python
from src.utils.data_utils import normalize_url

relative_url = "../products/item.html"
base = "https://example.com/category/"
absolute = normalize_url(relative_url, base)
# Result: "https://example.com/products/item.html"
```

#### `parse_date(date_string, formats=None)`
Parses date strings in various formats.

**Parameters:**
- `date_string` (str): Date string to parse
- `formats` (List[str], optional): Custom date formats to try

**Returns:** `datetime` object or None

**Supported Formats:**
- ISO 8601: "2024-01-15T10:30:00Z"
- US format: "01/15/2024"
- European format: "15/01/2024"
- Natural language: "January 15, 2024"
- Relative dates: "2 days ago"

**Example:**
```python
from src.utils.data_utils import parse_date

date_obj = parse_date("January 15, 2024")
iso_date = parse_date("2024-01-15T10:30:00Z")
relative = parse_date("2 days ago")
```

### Data Export

#### `export_to_csv(data, filename, options=None)`
Exports data to CSV format.

**Parameters:**
- `data` (List[Dict]): Data to export
- `filename` (str): Output filename
- `options` (Dict[str, Any], optional): Export options

**Options:**
- `delimiter`: CSV delimiter (default: ",")
- `encoding`: File encoding (default: "utf-8")
- `include_header`: Include column headers (default: True)
- `flatten_nested`: Flatten nested objects (default: True)
- `null_value`: Value for null fields (default: "")

**Returns:** `Path` - Path to exported file

#### `export_to_json(data, filename, options=None)`
Exports data to JSON format.

**Parameters:**
- `data` (Any): Data to export
- `filename` (str): Output filename
- `options` (Dict[str, Any], optional): Export options

**Options:**
- `indent`: JSON indentation (default: 2)
- `encoding`: File encoding (default: "utf-8")
- `ensure_ascii`: Ensure ASCII encoding (default: False)
- `include_metadata`: Include export metadata (default: True)

**Returns:** `Path` - Path to exported file

#### `export_to_excel(data, filename, options=None)`
Exports data to Excel (XLSX) format.

**Parameters:**
- `data` (List[Dict]): Data to export
- `filename` (str): Output filename
- `options` (Dict[str, Any], optional): Export options

**Options:**
- `sheet_name`: Worksheet name (default: "Data")
- `include_metadata`: Create metadata sheet (default: True)
- `auto_width`: Auto-adjust column widths (default: True)
- `freeze_header`: Freeze header row (default: True)

**Returns:** `Path` - Path to exported file

### Data Transformation

#### `flatten_dict(data, separator=".")`
Flattens nested dictionary structures.

**Parameters:**
- `data` (Dict): Dictionary to flatten
- `separator` (str): Key separator for nested keys

**Returns:** `Dict` - Flattened dictionary

**Example:**
```python
from src.utils.data_utils import flatten_dict

nested = {
    "product": {
        "name": "Laptop",
        "specs": {
            "cpu": "Intel i7",
            "ram": "16GB"
        }
    }
}

flat = flatten_dict(nested)
# Result: {
#     "product.name": "Laptop",
#     "product.specs.cpu": "Intel i7",
#     "product.specs.ram": "16GB"
# }
```

#### `unflatten_dict(data, separator=".")`
Reconstructs nested dictionary from flattened keys.

**Parameters:**
- `data` (Dict): Flattened dictionary
- `separator` (str): Key separator used in flattening

**Returns:** `Dict` - Nested dictionary

#### `merge_dicts(dict1, dict2, strategy="update")`
Merges two dictionaries with conflict resolution.

**Parameters:**
- `dict1` (Dict): First dictionary
- `dict2` (Dict): Second dictionary
- `strategy` (str): Merge strategy ("update", "keep", "combine")

**Strategies:**
- `update`: Second dict overwrites first
- `keep`: Keep first dict values on conflict
- `combine`: Combine values into lists

**Returns:** `Dict` - Merged dictionary

## Logging Utilities

**File:** `src/utils/logging_utils.py`

Provides logging configuration and helper functions.

### Logger Configuration

#### `get_logger(name, level=None)`
Gets a configured logger instance.

**Parameters:**
- `name` (str): Logger name (usually `__name__`)
- `level` (str, optional): Log level override

**Returns:** `logging.Logger` - Configured logger

**Example:**
```python
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)
logger.info("This is an info message")
logger.error("This is an error message")
```

#### `setup_logging(config=None)`
Sets up application-wide logging configuration.

**Parameters:**
- `config` (Dict[str, Any], optional): Logging configuration

**Default Configuration:**
- Level: INFO
- Format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
- File rotation: 10MB max, 5 backup files
- Console and file handlers

#### `log_performance(func)`
Decorator for logging function performance.

**Returns:** Decorator function

**Example:**
```python
from src.utils.logging_utils import log_performance

@log_performance
def expensive_operation():
    # Some time-consuming operation
    pass
```

### Structured Logging

#### `log_scraping_event(logger, event_type, data)`
Logs structured scraping events.

**Parameters:**
- `logger` (Logger): Logger instance
- `event_type` (str): Event type ("start", "success", "error", "retry")
- `data` (Dict[str, Any]): Event data

**Example:**
```python
from src.utils.logging_utils import log_scraping_event, get_logger

logger = get_logger(__name__)

log_scraping_event(logger, "start", {
    "url": "https://example.com",
    "template": "product_scraper",
    "job_id": "job-123"
})
```

#### `log_api_call(logger, method, endpoint, status_code, duration)`
Logs API call information.

**Parameters:**
- `logger` (Logger): Logger instance
- `method` (str): HTTP method
- `endpoint` (str): API endpoint
- `status_code` (int): Response status code
- `duration` (float): Request duration in seconds

### Error Logging

#### `log_exception(logger, exc, context=None)`
Logs exceptions with context information.

**Parameters:**
- `logger` (Logger): Logger instance
- `exc` (Exception): Exception to log
- `context` (Dict[str, Any], optional): Additional context

**Example:**
```python
from src.utils.logging_utils import log_exception, get_logger

logger = get_logger(__name__)

try:
    risky_operation()
except Exception as e:
    log_exception(logger, e, {
        "url": "https://example.com",
        "operation": "scraping"
    })
```

## Common Utility Functions

### String Utilities

#### `slugify(text)`
Converts text to URL-friendly slug.

**Parameters:**
- `text` (str): Text to convert

**Returns:** `str` - URL-friendly slug

**Example:**
```python
from src.utils.data_utils import slugify

slug = slugify("Product Name & Description!")
# Result: "product-name-description"
```

#### `truncate_text(text, max_length, suffix="...")`
Truncates text to specified length.

**Parameters:**
- `text` (str): Text to truncate
- `max_length` (int): Maximum length
- `suffix` (str): Suffix for truncated text

**Returns:** `str` - Truncated text

### File Utilities

#### `ensure_directory(path)`
Ensures directory exists, creating if necessary.

**Parameters:**
- `path` (Union[str, Path]): Directory path

**Returns:** `Path` - Directory path

#### `safe_filename(filename)`
Converts string to safe filename.

**Parameters:**
- `filename` (str): Original filename

**Returns:** `str` - Safe filename

**Example:**
```python
from src.utils.data_utils import safe_filename

safe = safe_filename("Product/Data: 2024.json")
# Result: "Product_Data_2024.json"
```

### Type Utilities

#### `is_url(text)`
Checks if text is a valid URL.

**Parameters:**
- `text` (str): Text to check

**Returns:** `bool` - True if valid URL

#### `is_email(text)`
Checks if text is a valid email address.

**Parameters:**
- `text` (str): Text to check

**Returns:** `bool` - True if valid email

#### `detect_data_type(value)`
Automatically detects data type of value.

**Parameters:**
- `value` (Any): Value to analyze

**Returns:** `str` - Detected type ("string", "number", "boolean", "date", "url", "email")

## Performance Utilities

### Caching

#### `lru_cache_with_ttl(maxsize=128, ttl=300)`
LRU cache with time-to-live expiration.

**Parameters:**
- `maxsize` (int): Maximum cache size
- `ttl` (int): Time-to-live in seconds

**Returns:** Decorator function

**Example:**
```python
from src.utils.data_utils import lru_cache_with_ttl

@lru_cache_with_ttl(maxsize=100, ttl=600)
def expensive_computation(param):
    # Expensive operation
    return result
```

### Retry Logic

#### `retry_on_exception(max_attempts=3, delay=1, backoff=2)`
Decorator for automatic retry with exponential backoff.

**Parameters:**
- `max_attempts` (int): Maximum retry attempts
- `delay` (float): Initial delay in seconds
- `backoff` (float): Backoff multiplier

**Returns:** Decorator function

**Example:**
```python
from src.utils.data_utils import retry_on_exception

@retry_on_exception(max_attempts=3, delay=1)
def unreliable_network_call():
    # Network operation that might fail
    pass
```

## Usage Examples

### Comprehensive Data Processing
```python
from src.utils.data_utils import (
    clean_text, extract_numbers, normalize_url, 
    flatten_dict, export_to_csv
)
from src.utils.validation_utils import validate_url

# Process scraped data
raw_data = [
    {
        "title": "  Product &amp; Name  ",
        "price": "Price: $29.99",
        "url": "../product/123",
        "details": {
            "color": "red",
            "size": "large"
        }
    }
]

processed_data = []
for item in raw_data:
    # Clean text
    clean_title = clean_text(item["title"], {
        "decode_entities": True,
        "strip_whitespace": True
    })
    
    # Extract price
    price = extract_numbers(item["price"], "float")
    
    # Normalize URL
    full_url = normalize_url(item["url"], "https://example.com/")
    
    # Validate URL
    url_valid = validate_url(full_url)["valid"]
    
    # Flatten nested data
    flat_item = flatten_dict({
        "title": clean_title,
        "price": price,
        "url": full_url if url_valid else None,
        **item["details"]
    })
    
    processed_data.append(flat_item)

# Export to CSV
export_path = export_to_csv(processed_data, "products.csv")
```

### Logging Setup
```python
from src.utils.logging_utils import (
    setup_logging, get_logger, log_scraping_event, log_performance
)

# Setup logging
setup_logging({
    "level": "INFO",
    "file": "logs/scraper.log",
    "console": True
})

logger = get_logger(__name__)

@log_performance
def scrape_page(url):
    logger.info(f"Starting to scrape {url}")
    
    log_scraping_event(logger, "start", {
        "url": url,
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        # Scraping logic
        result = perform_scraping(url)
        
        log_scraping_event(logger, "success", {
            "url": url,
            "items_found": len(result)
        })
        
        return result
        
    except Exception as e:
        log_scraping_event(logger, "error", {
            "url": url,
            "error": str(e)
        })
        raise
```

## See Also

- [Services Reference](services.md) - Services using these utilities
- [Scrapers Reference](scrapers.md) - Scrapers using these utilities
- [Configuration Reference](../configuration/) - Configuration utilities
- [Error Handling](../error-handling.md) - Error handling utilities