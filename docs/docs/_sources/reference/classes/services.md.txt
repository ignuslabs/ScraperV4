# Services Reference

This document provides complete reference for all service classes in ScraperV4, which handle business logic and coordinate between components.

## Service Architecture

ScraperV4 follows a service-oriented architecture where services encapsulate business logic and provide a clean interface for the web layer. All services inherit from `BaseService`.

### Service Hierarchy

```
BaseService (abstract)
├── ScrapingService
├── TemplateService
├── DataService
└── (Custom Services)
```

## BaseService

**File:** `src/services/base_service.py`

Base class for all services providing common functionality and dependency injection.

### Properties

**job_manager**
- **Type:** `JobManager`
- **Description:** Manages scraping jobs and their lifecycle
- **Access:** Read-only property

**template_manager**
- **Type:** `FileTemplateManager`
- **Description:** Handles template storage and retrieval
- **Access:** Read-only property

**result_storage**
- **Type:** `ResultStorage`
- **Description:** Manages scraped data storage
- **Access:** Read-only property

### Methods

#### `__init__()`
Initializes service with dependency injection from container.

```python
def __init__(self):
    """Initialize service with dependencies from container."""
```

## ScrapingService

**File:** `src/services/scraping_service.py`

Manages all scraping operations including job execution, URL validation, and progress tracking.

### Data Classes

#### JobData
Wrapper class providing attribute access to job data.

**Properties:**
- `id` (str): Unique job identifier
- `name` (str): Human-readable job name
- `status` (str): Current job status
- `progress` (int): Completion percentage (0-100)
- `items_scraped` (int): Number of items successfully scraped
- `items_failed` (int): Number of failed items
- `created_at` (datetime): Job creation timestamp
- `started_at` (datetime): Job start timestamp
- `completed_at` (datetime): Job completion timestamp
- `duration` (int): Job duration in seconds
- `error_message` (str): Error message if job failed

### Methods

#### `create_job(name, template_id, target_url, config=None, parameters=None)`
Creates a new scraping job.

**Parameters:**
- `name` (str): Human-readable job name
- `template_id` (str): Template identifier to use
- `target_url` (str): URL to scrape
- `config` (Dict[str, Any], optional): Job configuration
- `parameters` (Dict[str, Any], optional): Template parameters

**Returns:** `JobData` instance

**Example:**
```python
service = ScrapingService()
job = service.create_job(
    name="Product Scraping",
    template_id="product_template",
    target_url="https://example.com/products",
    config={"max_pages": 5}
)
```

#### `execute_job_async(job_id)`
Executes a scraping job asynchronously with progress updates.

**Parameters:**
- `job_id` (str): Job identifier

**Returns:** None (updates job status in storage)

**Features:**
- Real-time progress broadcasting
- Pagination support
- Error handling and recovery
- Template statistics updates

#### `stop_job(job_id)`
Stops a running scraping job.

**Parameters:**
- `job_id` (str): Job identifier

**Returns:** `bool` - True if successfully stopped

#### `get_job(job_id)`
Retrieves job information by ID.

**Parameters:**
- `job_id` (str): Job identifier

**Returns:** `JobData` instance or None

#### `scrape_with_template(template_name, target_url, parameters=None)`
Performs one-time scraping with a template.

**Parameters:**
- `template_name` (str): Template to use
- `target_url` (str): URL to scrape
- `parameters` (Dict[str, Any], optional): Template parameters

**Returns:** `Dict[str, Any]` with scraping results

**Response Format:**
```python
{
    "status": "success|failed|partial",
    "data": {...},  # Extracted data
    "url": "https://example.com",
    "template": "template_name",
    "parameters": {...},
    "scraped_at": "2024-01-01T12:00:00Z",
    "error": "Error message if failed"
}
```

#### `validate_scraping_target(url)`
Comprehensive URL validation with security checks.

**Parameters:**
- `url` (str): URL to validate

**Returns:** `Dict[str, Any]` with validation results

**Security Validations:**
- Scheme validation (HTTP/HTTPS only)
- Private IP range blocking
- Localhost blocking
- Suspicious pattern detection
- URL injection prevention
- Port blocking for internal services

**Response Format:**
```python
{
    "valid": True,
    "url": "https://example.com",
    "parsed_url": {
        "scheme": "https",
        "hostname": "example.com",
        "port": None,
        "path": "/",
        "query": "",
        "fragment": ""
    },
    "domain": "example.com",
    "security_risk": "low|medium|high",
    "warnings": [],
    "validation_checks": {
        "scheme_valid": True,
        "hostname_valid": True,
        "no_localhost": True,
        "no_private_ip": True,
        "no_credentials": True,
        "safe_port": True,
        "length_valid": True,
        "no_suspicious_patterns": True
    }
}
```

#### `preview_scraping(url, template_id)`
Previews scraping results without saving data.

**Parameters:**
- `url` (str): URL to preview
- `template_id` (str): Template to use

**Returns:** `Dict[str, Any]` with preview data

**Response Format:**
```python
{
    "url": "https://example.com",
    "template_id": "template_name",
    "success": True,
    "preview": {
        "count": 25,
        "success_rate": "85%",
        "sample_data": [
            {
                "field": "title",
                "value": "Sample Title",
                "type": "string"
            }
        ]
    },
    "preview_data": {
        "title": "Page Title",
        "items_found": 25,
        "selectors_matched": 5,
        "fields_extracted": ["title", "price", "description"],
        "validation_results": {...}
    }
}
```

## TemplateService

**File:** `src/services/template_service.py`

Manages template CRUD operations and validation.

### Data Classes

#### TemplateData
Wrapper class providing attribute access to template data.

**Properties:**
- `id` (str): Template identifier
- `name` (str): Template name
- `description` (str): Template description
- `version` (str): Template version
- `usage_count` (int): Number of times used
- `success_rate` (float): Success percentage
- `created_at` (str): Creation timestamp
- `selectors` (Dict): CSS selectors configuration
- `validation_rules` (Dict): Data validation rules
- `post_processing` (List): Post-processing rules
- `adaptive_selectors` (bool): Adaptive selector settings
- `fallback_selectors` (Dict): Fallback selector configuration

### Methods

#### `create_template(name, selectors, description=None, validation_rules=None, **kwargs)`
Creates a new template.

**Parameters:**
- `name` (str): Template name
- `selectors` (Dict[str, str]): CSS selectors
- `description` (str, optional): Template description
- `validation_rules` (Dict[str, Any], optional): Validation rules
- `**kwargs`: Additional template properties

**Returns:** `TemplateData` instance

#### `get_template(template_name)`
Retrieves a template by name.

**Parameters:**
- `template_name` (str): Template identifier

**Returns:** `TemplateData` instance or None

#### `update_template(template_name, updates)`
Updates an existing template.

**Parameters:**
- `template_name` (str): Template identifier
- `updates` (Dict[str, Any]): Fields to update

**Returns:** `bool` - True if successful

#### `delete_template(template_name)`
Deletes a template.

**Parameters:**
- `template_name` (str): Template identifier

**Returns:** `bool` - True if successful

#### `get_all_templates()`
Retrieves all templates.

**Returns:** `List[TemplateData]`

#### `validate_template(template_data)`
Validates template structure.

**Parameters:**
- `template_data` (Dict[str, Any]): Template configuration

**Returns:** `Dict[str, Any]` with validation results

**Response Format:**
```python
{
    "valid": True,
    "errors": []  # List of error messages
}
```

#### `test_template(template_name, test_url)`
Tests template selectors against a URL.

**Parameters:**
- `template_name` (str): Template to test
- `test_url` (str): URL to test against

**Returns:** `Dict[str, Any]` with test results

**Response Format:**
```python
{
    "success": True,
    "template": "template_name",
    "test_url": "https://example.com",
    "results": {
        "selector_results": {
            "title": {
                "found": True,
                "element_count": 1,
                "sample_value": "Page Title",
                "selector": "h1.title"
            }
        },
        "statistics": {
            "total_selectors": 5,
            "successful_selectors": 4,
            "success_rate": 80.0
        }
    },
    "success_rate": 80.0,
    "field_results": {...},
    "sample_data": {...}
}
```

## DataService

**File:** `src/services/data_service.py`

Handles data storage, retrieval, and export operations.

### Methods

#### `save_scraping_result(job_id, data, metadata=None)`
Saves scraped data to storage.

**Parameters:**
- `job_id` (str): Associated job ID
- `data` (Any): Scraped data
- `metadata` (Dict[str, Any], optional): Additional metadata

**Returns:** `str` - Result ID

#### `get_job_results(job_id, limit=100, offset=0)`
Retrieves results for a job with pagination.

**Parameters:**
- `job_id` (str): Job identifier
- `limit` (int): Maximum results to return
- `offset` (int): Number of results to skip

**Returns:** `List[Dict[str, Any]]` - Result records

#### `get_job_results_count(job_id)`
Gets total count of results for a job.

**Parameters:**
- `job_id` (str): Job identifier

**Returns:** `int` - Total result count

#### `export_job_results(job_id, format='csv')`
Exports job results to file.

**Parameters:**
- `job_id` (str): Job identifier
- `format` (str): Export format (csv, json, xlsx, xml)

**Returns:** `Path` - Path to exported file

**Supported Formats:**
- **CSV**: Comma-separated values with proper escaping
- **JSON**: Structured JSON with metadata
- **XLSX**: Excel spreadsheet with multiple sheets
- **XML**: Hierarchical XML structure

#### `process_scraped_data(data, processing_rules)`
Applies post-processing rules to data.

**Parameters:**
- `data` (Any): Raw scraped data
- `processing_rules` (List[Dict]): Processing rules to apply

**Returns:** `Dict[str, Any]` with processed data

**Processing Rule Types:**
- Text operations: strip, lowercase, uppercase, capitalize
- Numeric operations: extract_number, parse_float, parse_int
- List operations: unique, flatten, sort, filter
- Validation operations: validate_email, validate_url

## Service Container Integration

All services are managed by the dependency injection container:

```python
from src.core.container import container
from src.services.scraping_service import ScrapingService

# Get service instance
scraping_service = container.resolve(ScrapingService)

# Services are singletons - same instance returned
another_instance = container.resolve(ScrapingService)
assert scraping_service is another_instance
```

## Error Handling

Services implement consistent error handling patterns:

### Common Exceptions
- `ServiceError`: Base service exception
- `ValidationError`: Data validation failures
- `NotFoundError`: Resource not found
- `ConfigurationError`: Invalid configuration

### Error Response Format
```python
{
    "success": False,
    "error": "Descriptive error message",
    "error_code": "SERVICE_ERROR_001",
    "details": {
        "service": "ScrapingService",
        "method": "create_job",
        "parameters": {...}
    }
}
```

## Performance Considerations

### Caching
Services implement intelligent caching:
- Template caching for frequently used templates
- Result caching for repeated queries
- Configuration caching for settings

### Concurrency
Services are designed for concurrent access:
- Thread-safe operations
- Async/await support where applicable
- Connection pooling for database operations

### Resource Management
- Automatic cleanup of temporary files
- Memory usage monitoring
- Connection lifecycle management

## Usage Patterns

### Basic Service Usage
```python
from src.core.container import container
from src.services.scraping_service import ScrapingService

# Get service
service = container.resolve(ScrapingService)

# Create and execute job
job = service.create_job(
    name="My Scraping Job",
    template_id="product_template",
    target_url="https://example.com"
)

# Execute asynchronously
import asyncio
await service.execute_job_async(job.id)
```

### Template Management
```python
from src.services.template_service import TemplateService

service = container.resolve(TemplateService)

# Create template
template = service.create_template(
    name="my_template",
    selectors={
        "title": "h1.title",
        "price": ".price"
    },
    description="Product scraping template"
)

# Test template
results = service.test_template("my_template", "https://example.com")
```

### Data Export
```python
from src.services.data_service import DataService

service = container.resolve(DataService)

# Export to different formats
csv_file = service.export_job_results(job_id, "csv")
excel_file = service.export_job_results(job_id, "xlsx")
json_file = service.export_job_results(job_id, "json")
```

## Extension Points

Services can be extended through:

### Custom Services
```python
from src.services.base_service import BaseService

class CustomService(BaseService):
    def __init__(self):
        super().__init__()
    
    def custom_operation(self):
        # Custom business logic
        pass
```

### Service Decorators
```python
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        logger.info(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

class MonitoredScrapingService(ScrapingService):
    @monitor_performance
    def create_job(self, *args, **kwargs):
        return super().create_job(*args, **kwargs)
```

## Testing Services

Services are designed for easy testing:

```python
import pytest
from unittest.mock import Mock
from src.services.scraping_service import ScrapingService

def test_create_job():
    service = ScrapingService()
    
    # Mock dependencies
    service.job_manager = Mock()
    service.job_manager.create_job.return_value = {
        "id": "test-job-id",
        "name": "Test Job",
        "status": "pending"
    }
    
    # Test job creation
    job = service.create_job(
        name="Test Job",
        template_id="test_template",
        target_url="https://example.com"
    )
    
    assert job.id == "test-job-id"
    assert job.name == "Test Job"
```

## See Also

- [API Endpoints](../api/) - Web interface for services
- [Scrapers Reference](scrapers.md) - Scraper implementations used by services
- [Models Reference](models.md) - Data models used by services
- [Utilities Reference](utilities.md) - Helper functions used by services