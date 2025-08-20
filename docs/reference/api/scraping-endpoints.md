# Scraping Endpoints Reference

This document provides complete reference for all scraping-related API endpoints in ScraperV4.

## Job Management

### Start Scraping Job

**Function:** `start_scraping_job(job_data)`

Starts a new scraping job with the specified configuration.

**Parameters:**
- `job_data` (Dict[str, Any]): Job configuration object
  - `jobName` (str): Human-readable name for the job
  - `templateId` (str): Template identifier/name to use for scraping
  - `targetUrl` (str): URL to scrape
  - `config` (Dict[str, Any], optional): Job configuration options
    - `max_pages` (int): Maximum pages to scrape for pagination
    - `concurrent_requests` (int): Number of concurrent requests
    - `delay_between_pages` (List[int]): Min/max delay in seconds
  - `parameters` (Dict[str, Any], optional): Template-specific parameters

**Returns:**
```json
{
  "success": true,
  "job_id": "uuid-string",
  "message": "Scraping job started successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error description"
}
```

**Example:**
```javascript
const result = await eel.start_scraping_job({
  jobName: "Product Scraping - Amazon",
  templateId: "advanced_product_scraper",
  targetUrl: "https://example-store.com/products",
  config: {
    max_pages: 5,
    concurrent_requests: 2
  },
  parameters: {
    category_filter: "electronics"
  }
})();
```

### Stop Scraping Job

**Function:** `stop_scraping_job(job_id)`

Stops a currently running scraping job.

**Parameters:**
- `job_id` (int): Unique identifier of the job to stop

**Returns:**
```json
{
  "success": true,
  "message": "Scraping job stopped successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Job not found or already stopped"
}
```

**Example:**
```javascript
const result = await eel.stop_scraping_job(12345)();
```

### Get Job Status

**Function:** `get_job_status(job_id)`

Retrieves the current status and progress of a scraping job.

**Parameters:**
- `job_id` (int): Unique identifier of the job

**Returns:**
```json
{
  "success": true,
  "job": {
    "id": "uuid-string",
    "name": "Job Name",
    "status": "running|completed|failed|stopped|pending",
    "progress": 75,
    "items_scraped": 150,
    "items_failed": 5,
    "created_at": "2024-01-01T12:00:00Z",
    "started_at": "2024-01-01T12:01:00Z",
    "completed_at": null,
    "duration": 300,
    "error_message": null
  }
}
```

**Job Status Values:**
- `pending`: Job created but not yet started
- `running`: Job is currently executing
- `completed`: Job finished successfully
- `failed`: Job encountered an error and stopped
- `stopped`: Job was manually stopped

**Example:**
```javascript
const status = await eel.get_job_status(12345)();
if (status.success) {
  console.log(`Progress: ${status.job.progress}%`);
}
```

### Get Job Results

**Function:** `get_job_results(job_id, limit, offset)`

Retrieves scraped data results for a completed job with pagination support.

**Parameters:**
- `job_id` (int): Unique identifier of the job
- `limit` (int, optional): Maximum number of results to return (default: 100)
- `offset` (int, optional): Number of results to skip (default: 0)

**Returns:**
```json
{
  "success": true,
  "results": [
    {
      "id": "result-uuid",
      "source_url": "https://example.com/page1",
      "data": {
        "title": "Product Title",
        "price": 29.99,
        "description": "Product description..."
      },
      "scraped_at": "2024-01-01T12:05:00Z",
      "status": "success"
    }
  ],
  "total": 500
}
```

**Example:**
```javascript
// Get first 50 results
const results = await eel.get_job_results(12345, 50, 0)();

// Get next 50 results  
const nextResults = await eel.get_job_results(12345, 50, 50)();
```

## URL Validation and Preview

### Preview URL Scraping

**Function:** `preview_url(url, template_id)`

Previews what data would be scraped from a URL using a specific template without saving results.

**Parameters:**
- `url` (str): Target URL to preview
- `template_id` (str): Template identifier to use for preview

**Returns:**
```json
{
  "success": true,
  "preview": {
    "count": 25,
    "success_rate": "85%",
    "sample_data": [
      {
        "field": "title",
        "value": "Sample Product Title",
        "type": "string"
      },
      {
        "field": "prices",
        "value": ["$29.99", "$39.99", "$19.99"],
        "type": "list",
        "count": 3
      }
    ]
  }
}
```

**Preview Data Fields:**
- `count`: Number of items that would be scraped
- `success_rate`: Percentage of selectors that found data
- `sample_data`: Array of sample data showing field names and values

**Example:**
```javascript
const preview = await eel.preview_url(
  "https://example-store.com/products",
  "product_template"
)();
```

### Validate URL

**Function:** `validate_url(url)`

Validates if a URL is accessible and safe for scraping.

**Parameters:**
- `url` (str): URL to validate

**Returns:**
```json
{
  "success": true,
  "valid": true,
  "status_code": 200,
  "error": null
}
```

**Security Validations Performed:**
- Scheme validation (HTTP/HTTPS only)
- Private IP range blocking
- Localhost blocking  
- Suspicious pattern detection
- URL injection prevention
- Port blocking for internal services

**Example:**
```javascript
const validation = await eel.validate_url("https://example.com")();
if (validation.valid) {
  console.log("URL is safe to scrape");
}
```

### Test Selector

**Function:** `test_selector(url, selector)`

Tests a CSS selector against a URL to see what elements it matches.

**Parameters:**
- `url` (str): Target URL to test against
- `selector` (str): CSS selector to test

**Returns:**
```json
{
  "success": true,
  "matches": true,
  "count": 15,
  "sample_data": [
    "First matched element text",
    "Second matched element text",
    "Third matched element text"
  ]
}
```

**Example:**
```javascript
const test = await eel.test_selector(
  "https://example.com/products",
  ".product-title"
)();
console.log(`Found ${test.count} matching elements`);
```

## Progress Broadcasting

### Real-time Job Updates

ScraperV4 provides real-time progress updates via Eel's broadcasting system.

**Broadcast Function:** `broadcast_job_progress(data)`

**Progress Data Format:**
```json
{
  "job_id": "uuid-string",
  "progress": 45,
  "items_scraped": 120,
  "items_failed": 3,
  "timestamp": "2024-01-01T12:05:30Z"
}
```

**JavaScript Event Handling:**
```javascript
// Listen for progress updates
eel.expose(updateJobProgress);
function updateJobProgress(progressData) {
  console.log(`Job ${progressData.job_id}: ${progressData.progress}%`);
  // Update UI components
}
```

## Error Handling

All scraping endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Descriptive error message"
}
```

**Common Error Types:**
- `Template not found`: Invalid template_id provided
- `Invalid target URL`: URL validation failed
- `Job not found`: Invalid job_id provided
- `Scraping failed`: General scraping error
- `Template validation failed`: Template has configuration errors

## Rate Limiting and Concurrency

ScraperV4 implements built-in rate limiting and concurrency controls:

- **Default delay between requests**: 2 seconds (configurable)
- **Maximum concurrent jobs**: 3 (configurable)
- **Request timeout**: 30 seconds (configurable)
- **Maximum retries**: 3 (configurable)

These settings can be modified via the application settings endpoints.

## See Also

- [Status Endpoints](status-endpoints.md) - Job monitoring and health checks
- [Template Endpoints](template-endpoints.md) - Template management
- [Data Endpoints](data-endpoints.md) - Data export and retrieval
- [Configuration Reference](../configuration/environment-variables.md) - Scraping settings