# Scrapers Reference

This document provides complete reference for all scraper classes in ScraperV4, which handle web scraping operations using various fetching strategies.

## Scraper Architecture

ScraperV4 uses a modular scraper architecture with different fetcher types for various scraping scenarios. All scrapers inherit from `BaseScraper`.

### Scraper Hierarchy

```
BaseScraper (abstract)
├── TemplateScraper
├── StealthFetcher
├── FetcherManager
└── (Custom Scrapers)
```

## BaseScraper

**File:** `src/scrapers/base_scraper.py`

Abstract base class providing common scraping functionality and fetcher management.

### Properties

**fetcher_manager**
- **Type:** `FetcherManager`
- **Description:** Manages different fetcher types and configurations
- **Access:** Read-only property

### Methods

#### `__init__(fetcher_type=FetcherType.AUTO, fetcher_config=None)`
Initializes scraper with specified fetcher type and configuration.

**Parameters:**
- `fetcher_type` (FetcherType): Fetcher to use (AUTO, BASIC, ASYNC, STEALTH, PLAYWRIGHT)
- `fetcher_config` (Dict[str, Any], optional): Fetcher-specific configuration

#### `fetch_page(url, **kwargs)`
Synchronously fetches a web page using the configured fetcher.

**Parameters:**
- `url` (str): URL to fetch
- `**kwargs`: Additional fetcher-specific parameters

**Returns:** Scrapling response object

#### `fetch_page_async(url, **kwargs)`
Asynchronously fetches a web page.

**Parameters:**
- `url` (str): URL to fetch
- `**kwargs`: Additional fetcher-specific parameters

**Returns:** Awaitable Scrapling response object

#### `extract_data(response, selectors)`
Extracts data from response using CSS selectors.

**Parameters:**
- `response`: Scrapling response object
- `selectors` (Dict[str, Any]): CSS selectors configuration

**Returns:** `Dict[str, Any]` with extracted data

#### `validate_response(response)`
Validates response object for successful page load.

**Parameters:**
- `response`: Scrapling response object

**Returns:** `bool` - True if response is valid

## TemplateScraper

**File:** `src/scrapers/template_scraper.py`

Template-based scraper with adaptive selectors and advanced features.

### Features
- Template-driven scraping
- Adaptive selector learning
- Fallback selector support
- Post-processing and validation
- Pagination support
- Async scraping capabilities

### Methods

#### `__init__(template=None)`
Initializes template scraper with configuration.

**Parameters:**
- `template` (Dict[str, Any], optional): Scraping template

**Template Structure:**
```python
{
    "name": "template_name",
    "selectors": {
        "field_name": {
            "selector": "CSS_SELECTOR",
            "type": "text|all|attribute|html",
            "attribute": "attr_name",  # for attribute type
            "fallback_selectors": ["fallback1", "fallback2"]
        }
    },
    "fetcher_config": {
        "type": "auto|basic|async|stealth|playwright",
        "stealth": {...},
        "playwright": {...}
    },
    "post_processing": [...],
    "validation_rules": {...},
    "pagination": {...}
}
```

#### `set_template(template)`
Updates the scraping template.

**Parameters:**
- `template` (Dict[str, Any]): New template configuration

#### `scrape(url, **kwargs)`
Synchronously scrapes URL using template.

**Parameters:**
- `url` (str): URL to scrape
- `**kwargs`: Additional parameters

**Returns:** `Dict[str, Any]` with scraping results

**Response Format:**
```python
{
    "url": "https://example.com",
    "status": "success|failed|partial",
    "data": {
        "field1": "extracted_value1",
        "field2": ["list", "of", "values"],
        "field3": 123.45
    },
    "items_count": 1,
    "template_name": "template_name",
    "timestamp": 1640995200.0,
    "validation_errors": []  # if status is partial
}
```

#### `scrape_async(url, **kwargs)`
Asynchronously scrapes URL using template.

**Parameters:**
- `url` (str): URL to scrape
- `**kwargs`: Additional parameters

**Returns:** Awaitable `Dict[str, Any]` with scraping results

#### `scrape_with_pagination(url, **kwargs)`
Scrapes multiple pages following pagination links.

**Parameters:**
- `url` (str): Starting URL
- `**kwargs`: Additional parameters including `max_pages`

**Returns:** `Dict[str, Any]` with combined results

**Response Format:**
```python
{
    "url": "https://example.com/page1",
    "status": "success",
    "pages_scraped": 5,
    "total_items": 150,
    "results": [
        {"url": "page1", "data": {...}},
        {"url": "page2", "data": {...}},
        ...
    ],
    "template_name": "template_name"
}
```

#### `scrape_with_pagination_async(url, **kwargs)`
Asynchronously scrapes multiple pages with pagination.

**Parameters:**
- `url` (str): Starting URL
- `**kwargs`: Additional parameters

**Returns:** Awaitable `Dict[str, Any]` with combined results

#### `extract_data_adaptive(response, selectors)`
Extracts data using adaptive selectors with self-healing.

**Parameters:**
- `response`: Scrapling response object
- `selectors` (Dict[str, Any]): Selectors configuration

**Returns:** `Dict[str, Any]` with extracted data

**Features:**
- Automatic fallback to alternative selectors
- Learning from successful extractions
- Selector adaptation based on page structure changes

#### `validate_template()`
Validates template structure and selectors.

**Returns:** `Dict[str, Any]` with validation results

**Response Format:**
```python
{
    "valid": True,
    "errors": []  # List of validation errors
}
```

#### `test_selectors(url)`
Tests template selectors against a URL.

**Parameters:**
- `url` (str): URL to test selectors against

**Returns:** `Dict[str, Any]` with test results

**Response Format:**
```python
{
    "selector_results": {
        "field_name": {
            "found": True,
            "element_count": 5,
            "sample_value": "Sample extracted text",
            "selector": "h1.title"
        }
    },
    "statistics": {
        "total_selectors": 10,
        "successful_selectors": 8,
        "success_rate": 80.0
    }
}
```

## FetcherManager

**File:** `src/scrapers/fetcher_manager.py`

Manages different fetcher types and their configurations.

### FetcherType Enum

```python
class FetcherType(Enum):
    AUTO = "auto"           # Automatically choose best fetcher
    BASIC = "basic"         # Simple HTTP requests
    ASYNC = "async"         # Asynchronous HTTP requests
    STEALTH = "stealth"     # Browser-based with anti-detection
    PLAYWRIGHT = "playwright"  # Full browser automation
```

### Methods

#### `__init__(default_type=FetcherType.AUTO)`
Initializes fetcher manager.

**Parameters:**
- `default_type` (FetcherType): Default fetcher to use

#### `get_fetcher(fetcher_type=None, config=None)`
Gets fetcher instance for specified type.

**Parameters:**
- `fetcher_type` (FetcherType, optional): Fetcher type to get
- `config` (Dict[str, Any], optional): Fetcher configuration

**Returns:** Configured fetcher instance

#### `set_custom_config(fetcher_type, config)`
Sets custom configuration for a fetcher type.

**Parameters:**
- `fetcher_type` (FetcherType): Fetcher to configure
- `config` (Dict[str, Any]): Configuration to apply

#### `auto_select_fetcher(url, requirements=None)`
Automatically selects best fetcher for URL and requirements.

**Parameters:**
- `url` (str): Target URL
- `requirements` (Dict[str, Any], optional): Scraping requirements

**Returns:** `FetcherType` - Selected fetcher type

**Selection Criteria:**
- JavaScript requirement detection
- Anti-bot protection analysis
- Site complexity assessment
- Performance requirements

## StealthFetcher

**File:** `src/scrapers/stealth_fetcher.py`

Advanced stealth fetcher with anti-detection capabilities.

### Features
- Browser fingerprint randomization
- Human behavior simulation
- Anti-bot detection evasion
- Proxy integration
- Challenge solving capabilities

### Configuration Options

#### Basic Stealth Configuration
```python
{
    "headless": True,
    "humanize": True,
    "block_webrtc": True,
    "spoof_canvas": True,
    "os_randomization": True,
    "google_search": True,
    "disable_ads": True
}
```

#### Advanced Stealth Configuration
```python
{
    "stealth_level": "high",
    "anti_detection": {
        "webdriver_detection": True,
        "bot_detection": True,
        "fingerprint_resistance": True
    },
    "behavior_simulation": {
        "mouse_movements": True,
        "scroll_behavior": True,
        "typing_patterns": True,
        "reading_patterns": True
    },
    "traffic_masking": {
        "google_search": True,
        "referrer_spoofing": True,
        "random_delays": True,
        "session_simulation": True
    }
}
```

### Methods

#### `fetch(url, **kwargs)`
Fetches URL with stealth capabilities.

**Parameters:**
- `url` (str): URL to fetch
- `**kwargs`: Stealth-specific parameters

**Returns:** Scrapling response object

#### `solve_challenges(page)`
Automatically solves common anti-bot challenges.

**Parameters:**
- `page`: Browser page object

**Returns:** `bool` - True if challenges were solved

#### `randomize_fingerprint()`
Randomizes browser fingerprint for this session.

#### `simulate_human_behavior(page)`
Simulates human browsing behavior.

**Parameters:**
- `page`: Browser page object

## Fetcher Configurations

### Basic Fetcher
Simple HTTP requests with basic headers.

```python
{
    "timeout": 30,
    "headers": {
        "User-Agent": "ScraperV4/1.0",
        "Accept": "text/html,application/xhtml+xml"
    },
    "follow_redirects": True,
    "max_redirects": 5
}
```

### Async Fetcher
Asynchronous HTTP with advanced features.

```python
{
    "timeout": 30,
    "concurrent_requests": 5,
    "retry_attempts": 3,
    "retry_delay": [1, 3],
    "connection_pool_size": 100,
    "headers": {...}
}
```

### Stealth Fetcher
Browser-based with anti-detection.

```python
{
    "headless": True,
    "humanize": True,
    "stealth_level": "medium",
    "wait_for_selector": ".content",
    "wait_for_timeout": 10,
    "screenshot": False,
    "full_page_screenshot": False,
    "block_resources": ["image", "font"],
    "proxy": {
        "enabled": True,
        "type": "socks5",
        "host": "proxy.example.com",
        "port": 1080
    }
}
```

### Playwright Fetcher
Full browser automation with Playwright.

```python
{
    "headless": True,
    "browser": "chromium",
    "viewport": {
        "width": 1920,
        "height": 1080
    },
    "network_idle": True,
    "wait_for_selector": ".content",
    "block_resources": ["image", "font", "media"],
    "extra_headers": {
        "Accept-Language": "en-US"
    },
    "geolocation": {
        "latitude": 40.7128,
        "longitude": -74.0060
    }
}
```

## Data Extraction

### Selector Types

#### Text Extraction
```python
{
    "title": {
        "selector": "h1.page-title",
        "type": "text"
    }
}
```

#### Attribute Extraction
```python
{
    "image_url": {
        "selector": "img.hero",
        "type": "attribute",
        "attribute": "src"
    }
}
```

#### Multiple Elements
```python
{
    "product_list": {
        "selector": ".product-item",
        "type": "all"
    }
}
```

#### HTML Content
```python
{
    "description": {
        "selector": ".product-description",
        "type": "html"
    }
}
```

### Fallback Selectors

```python
{
    "price": {
        "selector": ".price-current",
        "type": "text",
        "fallback_selectors": [
            ".price-now",
            ".cost",
            "[data-price]",
            ".product-price"
        ]
    }
}
```

### Adaptive Selectors

Adaptive selectors automatically learn and improve:

```python
{
    "adaptive_selectors": {
        "enabled": True,
        "learning_mode": True,
        "similarity_threshold": 0.85,
        "confidence_threshold": 0.90
    }
}
```

## Post-Processing

### Text Operations
```python
{
    "post_processing": [
        {
            "type": "strip",
            "field": "title"
        },
        {
            "type": "lowercase",
            "field": "category"
        },
        {
            "type": "replace",
            "field": "description",
            "pattern": "\\s+",
            "replacement": " "
        }
    ]
}
```

### Numeric Operations
```python
{
    "post_processing": [
        {
            "type": "extract_number",
            "field": "price"
        },
        {
            "type": "parse_float",
            "field": "rating"
        }
    ]
}
```

### List Operations
```python
{
    "post_processing": [
        {
            "type": "unique",
            "field": "tags"
        },
        {
            "type": "sort",
            "field": "categories"
        }
    ]
}
```

## Validation

### Field Validation
```python
{
    "validation_rules": {
        "required_fields": ["title", "price"],
        "field_types": {
            "title": "string",
            "price": "number",
            "tags": "list"
        },
        "field_patterns": {
            "email": "^[\\w\\.-]+@[\\w\\.-]+\\.[a-zA-Z]{2,}$"
        },
        "field_ranges": {
            "price": [0, 10000],
            "rating": [0, 5]
        }
    }
}
```

## Pagination

### Basic Pagination
```python
{
    "pagination": {
        "enabled": True,
        "next_selector": "a.next-page",
        "max_pages": 10,
        "delay_between_pages": [1, 3]
    }
}
```

### Advanced Pagination
```python
{
    "pagination": {
        "enabled": True,
        "next_selector": "a.pagination-next",
        "max_pages": 50,
        "delay_between_pages": [2, 5],
        "stop_conditions": [
            "no_new_data",
            "duplicate_detection",
            "max_pages_reached"
        ],
        "url_pattern": "https://example.com/page/{page}",
        "page_parameter": "page",
        "start_page": 1
    }
}
```

## Error Handling

### Scraper Exceptions
```python
class ScraperError(Exception):
    """Base scraper exception"""

class FetchError(ScraperError):
    """Failed to fetch page"""

class ExtractionError(ScraperError):
    """Failed to extract data"""

class ValidationError(ScraperError):
    """Data validation failed"""

class TemplateError(ScraperError):
    """Template configuration error"""
```

### Error Response Format
```python
{
    "url": "https://example.com",
    "status": "failed",
    "error": "Fetch timeout after 30 seconds",
    "error_code": "FETCH_TIMEOUT",
    "template_name": "product_scraper",
    "retry_count": 3,
    "timestamp": 1640995200.0
}
```

## Performance Optimization

### Concurrent Scraping
```python
import asyncio
from src.scrapers.template_scraper import TemplateScraper

async def scrape_multiple_urls(urls, template):
    scraper = TemplateScraper(template)
    
    tasks = [scraper.scrape_async(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results
```

### Connection Pooling
```python
{
    "async_config": {
        "connection_pool_size": 100,
        "max_connections_per_host": 10,
        "connection_timeout": 30,
        "read_timeout": 60
    }
}
```

### Resource Management
```python
{
    "resource_optimization": {
        "block_images": True,
        "block_fonts": True,
        "block_media": True,
        "compress_responses": True,
        "cache_responses": True
    }
}
```

## Usage Examples

### Basic Template Scraping
```python
from src.scrapers.template_scraper import TemplateScraper

template = {
    "name": "basic_scraper",
    "selectors": {
        "title": "h1",
        "description": ".description"
    }
}

scraper = TemplateScraper(template)
result = scraper.scrape("https://example.com")
```

### Advanced Stealth Scraping
```python
template = {
    "name": "stealth_scraper",
    "fetcher_config": {
        "type": "stealth",
        "stealth": {
            "headless": True,
            "humanize": True,
            "stealth_level": "high",
            "google_search": True
        }
    },
    "selectors": {
        "products": {
            "selector": ".product",
            "type": "all"
        }
    }
}

scraper = TemplateScraper(template)
result = scraper.scrape("https://protected-site.com")
```

### Pagination Scraping
```python
template = {
    "name": "pagination_scraper",
    "selectors": {
        "items": ".item-list .item"
    },
    "pagination": {
        "enabled": True,
        "next_selector": ".next-page",
        "max_pages": 5
    }
}

scraper = TemplateScraper(template)
result = scraper.scrape_with_pagination("https://example.com/page1")
```

## See Also

- [Services Reference](services.md) - Service layer using scrapers
- [Template Schema](../configuration/template-schema.md) - Template configuration reference
- [Stealth Options](../configuration/stealth-options.md) - Stealth configuration options
- [Utilities Reference](utilities.md) - Helper functions and utilities