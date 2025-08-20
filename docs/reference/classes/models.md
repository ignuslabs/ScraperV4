# Models Reference

This document provides complete reference for all data models and storage classes in ScraperV4, which handle data persistence and job management.

## Data Management Architecture

ScraperV4 uses a file-based data management system with JSON storage for flexibility and simplicity. The architecture includes job management, template storage, and result storage.

### Core Components

```
JobManager - Manages scraping jobs lifecycle
├── Job data storage (JSON files)
├── Status tracking
└── Progress monitoring

TemplateManager - Handles template CRUD operations
├── Template storage (JSON files)
├── Validation and testing
└── Statistics tracking

ResultStorage - Manages scraped data
├── Result data storage
├── Export capabilities
└── Data processing
```

## JobManager

**File:** `src/data/job_manager.py`

Manages scraping jobs using file-based storage with JSON format.

### Job Data Structure

```python
{
    "id": "uuid-string",
    "name": "Human readable job name",
    "template_name": "template_identifier",
    "target_url": "https://example.com",
    "config": {
        "max_pages": 5,
        "concurrent_requests": 2,
        "delay_between_pages": [1, 3]
    },
    "parameters": {
        "category_filter": "electronics",
        "price_range": [10, 100]
    },
    "status": "pending|running|completed|failed|stopped",
    "progress": 75,
    "items_scraped": 150,
    "items_failed": 5,
    "created_at": "2024-01-01T12:00:00.000000",
    "started_at": "2024-01-01T12:01:00.000000",
    "completed_at": "2024-01-01T12:30:00.000000",
    "error_message": null,
    "retry_count": 0,
    "duration": 1800,
    "result_id": "result-uuid"
}
```

### Job Status Values

- **pending**: Job created but not yet started
- **running**: Job is currently executing
- **completed**: Job finished successfully
- **failed**: Job encountered an error and stopped
- **stopped**: Job was manually stopped by user

### Methods

#### `__init__()`
Initializes job manager with configured storage directory.

```python
def __init__(self):
    """Initialize with jobs directory from config."""
```

#### `create_job(name, template_name, target_url, job_config=None, parameters=None)`
Creates a new scraping job with unique ID.

**Parameters:**
- `name` (str): Human-readable job name
- `template_name` (str): Template identifier to use
- `target_url` (str): URL to scrape
- `job_config` (Dict[str, Any], optional): Job-specific configuration
- `parameters` (Dict[str, Any], optional): Template parameters

**Returns:** `Dict[str, Any]` - Complete job data

**Example:**
```python
job_manager = JobManager()
job = job_manager.create_job(
    name="Product Scraping - Electronics",
    template_name="product_scraper",
    target_url="https://store.com/electronics",
    job_config={
        "max_pages": 10,
        "concurrent_requests": 3
    },
    parameters={
        "category": "smartphones",
        "min_price": 100
    }
)
```

#### `get_job(job_id)`
Retrieves job data by ID.

**Parameters:**
- `job_id` (str): Unique job identifier

**Returns:** `Dict[str, Any]` or None if not found

#### `update_job(job_id, updates)`
Updates job data with new values.

**Parameters:**
- `job_id` (str): Job identifier
- `updates` (Dict[str, Any]): Fields to update

**Returns:** `bool` - True if successful

#### `list_jobs(status=None)`
Lists all jobs with optional status filtering.

**Parameters:**
- `status` (str, optional): Filter by job status

**Returns:** `List[Dict[str, Any]]` - List of jobs sorted by creation date

#### `delete_job(job_id)`
Permanently deletes a job.

**Parameters:**
- `job_id` (str): Job identifier

**Returns:** `bool` - True if successful

#### `update_job_status(job_id, status, error_message=None)`
Updates job status with automatic timestamp management.

**Parameters:**
- `job_id` (str): Job identifier
- `status` (str): New status
- `error_message` (str, optional): Error message for failed jobs

**Returns:** `bool` - True if successful

**Automatic Timestamps:**
- Setting status to "running" sets `started_at`
- Setting status to "completed" or "failed" sets `completed_at`

#### `update_job_progress(job_id, progress, items_scraped=0, items_failed=0)`
Updates job progress metrics.

**Parameters:**
- `job_id` (str): Job identifier
- `progress` (int): Completion percentage (0-100)
- `items_scraped` (int): Number of successfully scraped items
- `items_failed` (int): Number of failed items

**Returns:** `bool` - True if successful

## TemplateManager

**File:** `src/data/template_manager.py`

Handles template storage, validation, and statistics tracking.

### Template Data Structure

```python
{
    "name": "template_identifier",
    "description": "Template description",
    "version": "2.0.0",
    "selectors": {
        "field_name": {
            "selector": "CSS_SELECTOR",
            "type": "text|all|attribute|html",
            "auto_save": true,
            "fallback_selectors": ["fallback1", "fallback2"],
            "attribute": "href",
            "required": true,
            "default": "default_value"
        }
    },
    "fetcher_config": {
        "type": "auto|basic|async|stealth|playwright",
        "basic": {...},
        "async": {...},
        "stealth": {...},
        "playwright": {...}
    },
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
    },
    "post_processing": [
        {
            "type": "strip|lowercase|extract_number|replace",
            "field": "field_name",
            "pattern": "regex_pattern",
            "replacement": "replacement_text"
        }
    ],
    "pagination": {
        "enabled": true,
        "next_selector": "a.next-page",
        "max_pages": 10,
        "delay_between_pages": [1, 3]
    },
    "adaptive_selectors": {
        "enabled": true,
        "learning_mode": true,
        "similarity_threshold": 0.85
    },
    "fallback_selectors": {
        "enabled": true,
        "max_attempts": 3
    },
    "requirements": {
        "javascript_required": false,
        "stealth_required": true,
        "anti_bot_protection": true
    },
    "is_active": true,
    "usage_count": 25,
    "success_rate": 94.5,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### Methods

#### `load_template(template_name)`
Loads template by name from storage.

**Parameters:**
- `template_name` (str): Template identifier

**Returns:** `Dict[str, Any]` or None if not found

#### `save_template(template_name, template_data)`
Saves template to storage.

**Parameters:**
- `template_name` (str): Template identifier
- `template_data` (Dict[str, Any]): Template configuration

**Returns:** `bool` - True if successful

#### `create_template(name, selectors, description=None, validation_rules=None)`
Creates a new template with default values.

**Parameters:**
- `name` (str): Template name
- `selectors` (Dict[str, Any]): CSS selectors configuration
- `description` (str, optional): Template description
- `validation_rules` (Dict[str, Any], optional): Validation rules

**Returns:** `Dict[str, Any]` - Complete template data

#### `list_templates()`
Lists all available templates.

**Returns:** `List[Dict[str, Any]]` - All templates with metadata

#### `delete_template(template_name)`
Deletes a template from storage.

**Parameters:**
- `template_name` (str): Template identifier

**Returns:** `bool` - True if successful

#### `update_template_stats(template_name, success)`
Updates template usage statistics.

**Parameters:**
- `template_name` (str): Template identifier
- `success` (bool): Whether the usage was successful

**Updates:**
- Increments `usage_count`
- Recalculates `success_rate`
- Updates `updated_at` timestamp

#### `validate_template_structure(template_data)`
Validates template configuration structure.

**Parameters:**
- `template_data` (Dict[str, Any]): Template to validate

**Returns:** `Dict[str, Any]` with validation results

**Response Format:**
```python
{
    "valid": True,
    "errors": [],
    "warnings": [],
    "suggestions": []
}
```

## ResultStorage

**File:** `src/data/result_storage.py`

Manages scraped data storage and retrieval with export capabilities.

### Result Data Structure

```python
{
    "id": "result-uuid",
    "job_id": "job-uuid",
    "source_url": "https://example.com/page1",
    "data": {
        "title": "Scraped Title",
        "price": 29.99,
        "description": "Product description",
        "images": ["image1.jpg", "image2.jpg"],
        "metadata": {
            "category": "electronics",
            "brand": "BrandName"
        }
    },
    "metadata": {
        "template_used": "product_scraper",
        "fetch_method": "stealth",
        "response_time": 1.2,
        "status_code": 200,
        "retry_count": 0,
        "processing_time": 0.5,
        "page_size": 45678,
        "selectors_used": {
            "title": "h1.product-title",
            "price": ".price-current"
        }
    },
    "scraped_at": "2024-01-01T12:00:00Z",
    "status": "success|failed|partial",
    "validation_results": {
        "required_fields_present": true,
        "type_validation_passed": true,
        "custom_validation_passed": true,
        "errors": []
    },
    "processing_applied": [
        {
            "type": "strip",
            "field": "title"
        },
        {
            "type": "extract_number",
            "field": "price"
        }
    ]
}
```

### Methods

#### `save_result(job_id, url, data, metadata=None)`
Saves a single scraping result.

**Parameters:**
- `job_id` (str): Associated job ID
- `url` (str): Source URL
- `data` (Dict[str, Any]): Scraped data
- `metadata` (Dict[str, Any], optional): Additional metadata

**Returns:** `str` - Result ID

#### `get_results(job_id, limit=100, offset=0)`
Retrieves results for a job with pagination.

**Parameters:**
- `job_id` (str): Job identifier
- `limit` (int): Maximum results to return
- `offset` (int): Number of results to skip

**Returns:** `List[Dict[str, Any]]` - Result records

#### `get_result_count(job_id)`
Gets total number of results for a job.

**Parameters:**
- `job_id` (str): Job identifier

**Returns:** `int` - Total result count

#### `delete_results(job_id)`
Deletes all results for a job.

**Parameters:**
- `job_id` (str): Job identifier

**Returns:** `bool` - True if successful

#### `export_results(job_id, format='csv', output_path=None)`
Exports job results to file.

**Parameters:**
- `job_id` (str): Job identifier
- `format` (str): Export format (csv, json, xlsx, xml)
- `output_path` (str, optional): Custom output path

**Returns:** `Path` - Path to exported file

**Export Formats:**
- **CSV**: Flat structure with nested objects as JSON strings
- **JSON**: Complete structure with metadata
- **XLSX**: Excel file with data and metadata sheets
- **XML**: Hierarchical XML structure

## Configuration Models

### AppConfig

**File:** `src/core/config.py`

Main application configuration using Pydantic models.

```python
class AppConfig(BaseModel):
    app_name: str = "ScraperV4"
    version: str = "1.0.0"
    data_folder: str = "data"
    templates_folder: str = "templates"
    
    storage: StorageConfig = StorageConfig()
    scraping: ScrapingConfig = ScrapingConfig()
    scrapling: ScraplingConfig = ScraplingConfig()
    eel: EelConfig = EelConfig()
    logging: LoggingConfig = LoggingConfig()
```

### StorageConfig

Configuration for file storage locations.

```python
class StorageConfig(BaseModel):
    data_folder: str = "data"
    jobs_folder: str = "data/jobs"
    results_folder: str = "data/results"
    templates_folder: str = "templates"
```

### ScrapingConfig

General scraping behavior configuration.

```python
class ScrapingConfig(BaseModel):
    default_delay: float = 2.0
    max_retries: int = 3
    timeout: int = 30
    stealth_mode: bool = True
    concurrent_jobs: int = 3
    user_agent: str = "ScraperV4/1.0"
```

### ScraplingConfig

Scrapling-specific configuration.

```python
class ScraplingConfig(BaseModel):
    stealth_mode: bool = True
    user_agent: str = "ScraperV4/1.0"
    timeout: int = 30
    max_retries: int = 3
    delay_range: tuple = (1, 3)
```

### EelConfig

Web interface configuration.

```python
class EelConfig(BaseModel):
    port: int = 8080
    debug: bool = True
    web_folder: str = "web"
    allowed_extensions: List[str] = ['.html', '.css', '.js', '.png', '.jpg', '.gif']
```

### LoggingConfig

Logging system configuration.

```python
class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: str = "logs/scraperv4.log"
    max_bytes: int = 10_000_000
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## Data Validation

### Field Types
- **string**: Text data
- **number**: Numeric data (int or float)
- **integer**: Integer values only
- **boolean**: True/false values
- **list**: Array of values
- **object**: Nested dictionary
- **datetime**: ISO formatted datetime strings

### Validation Rules

#### Required Fields
```python
{
    "required_fields": ["title", "price", "url"]
}
```

#### Type Validation
```python
{
    "field_types": {
        "title": "string",
        "price": "number",
        "published_date": "datetime",
        "is_featured": "boolean",
        "tags": "list",
        "metadata": "object"
    }
}
```

#### Pattern Validation
```python
{
    "field_patterns": {
        "email": "^[\\w\\.-]+@[\\w\\.-]+\\.[a-zA-Z]{2,}$",
        "phone": "^\\+?[1-9]\\d{1,14}$",
        "url": "^https?://[\\w\\.-]+",
        "price": "^\\$?\\d+\\.\\d{2}$"
    }
}
```

#### Range Validation
```python
{
    "field_ranges": {
        "price": [0, 10000],
        "rating": [0, 5],
        "quantity": [1, null]  # null means no upper limit
    }
}
```

## Data Processing

### Post-Processing Operations

#### Text Operations
```python
{
    "type": "strip",           # Remove whitespace
    "field": "title"
},
{
    "type": "lowercase",       # Convert to lowercase
    "field": "category"
},
{
    "type": "replace",         # Replace patterns
    "field": "description",
    "pattern": "\\s+",
    "replacement": " "
}
```

#### Numeric Operations
```python
{
    "type": "extract_number",  # Extract first number
    "field": "price"
},
{
    "type": "parse_float",     # Convert to float
    "field": "rating"
},
{
    "type": "round",           # Round decimals
    "field": "price",
    "decimals": 2
}
```

#### List Operations
```python
{
    "type": "unique",          # Remove duplicates
    "field": "tags"
},
{
    "type": "sort",            # Sort elements
    "field": "categories"
},
{
    "type": "limit",           # Limit number of items
    "field": "images",
    "max_items": 5
}
```

## File Storage Structure

### Directory Layout
```
data/
├── jobs/
│   ├── {job-uuid-1}.json
│   ├── {job-uuid-2}.json
│   └── ...
├── results/
│   ├── {job-uuid-1}/
│   │   ├── result-1.json
│   │   ├── result-2.json
│   │   └── metadata.json
│   └── {job-uuid-2}/
└── exports/
    ├── {job-name}_{timestamp}.csv
    ├── {job-name}_{timestamp}.xlsx
    └── ...

templates/
├── template1.json
├── template2.json
└── ...
```

### File Naming Conventions
- **Jobs**: `{uuid}.json`
- **Results**: `result-{index}.json`
- **Templates**: `{template-name}.json`
- **Exports**: `{job-name}_{timestamp}.{format}`

## Error Handling

### Data Exceptions
```python
class DataError(Exception):
    """Base data operation exception"""

class StorageError(DataError):
    """File storage operation failed"""

class ValidationError(DataError):
    """Data validation failed"""

class ExportError(DataError):
    """Data export failed"""

class CorruptedDataError(DataError):
    """Data file is corrupted"""
```

### Recovery Mechanisms
- Automatic backup creation before updates
- Corrupted file detection and recovery
- Partial data recovery from backups
- Graceful degradation when storage unavailable

## Performance Considerations

### File Operations
- Atomic writes to prevent corruption
- File locking for concurrent access
- Compression for large result sets
- Lazy loading for memory efficiency

### Indexing
- In-memory indexes for frequently accessed data
- LRU cache for recent templates and jobs
- Efficient filtering and sorting

### Cleanup
- Automatic cleanup of old exports
- Configurable data retention policies
- Background cleanup processes

## Usage Examples

### Job Management
```python
from src.data.job_manager import JobManager

job_manager = JobManager()

# Create job
job = job_manager.create_job(
    name="E-commerce Scraping",
    template_name="product_template",
    target_url="https://store.com/products"
)

# Update progress
job_manager.update_job_progress(
    job["id"], 
    progress=50, 
    items_scraped=100
)

# Complete job
job_manager.update_job_status(job["id"], "completed")
```

### Template Management
```python
from src.data.template_manager import FileTemplateManager

template_manager = FileTemplateManager()

# Create template
template = template_manager.create_template(
    name="blog_scraper",
    selectors={
        "title": "h1.post-title",
        "content": ".post-content",
        "author": ".author-name"
    },
    description="Blog post scraper"
)

# Update statistics
template_manager.update_template_stats("blog_scraper", success=True)
```

### Result Storage
```python
from src.data.result_storage import ResultStorage

result_storage = ResultStorage()

# Save result
result_id = result_storage.save_result(
    job_id="job-uuid",
    url="https://example.com/page1",
    data={
        "title": "Article Title",
        "content": "Article content..."
    }
)

# Export results
export_path = result_storage.export_results(
    job_id="job-uuid",
    format="xlsx"
)
```

## See Also

- [Services Reference](services.md) - Services using these models
- [API Endpoints](../api/) - Web interface for data operations
- [Configuration Reference](../configuration/) - Configuration models
- [Error Handling](../error-handling.md) - Error codes and handling