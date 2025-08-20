# Data Endpoints Reference

This document provides complete reference for all data export and retrieval API endpoints in ScraperV4.

## Data Export

### Export Job Results

**Function:** `export_results(job_id, format)`

Exports scraped data from a completed job to various file formats.

**Parameters:**
- `job_id` (str): Unique identifier of the completed job
- `format` (str): Export format (`csv`, `json`, `xlsx`, `xml`)

**Supported Export Formats:**
- `csv`: Comma-separated values (default)
- `json`: JavaScript Object Notation
- `xlsx`: Microsoft Excel spreadsheet
- `xml`: Extensible Markup Language

**Returns:**
```json
{
  "success": true,
  "file_path": "/absolute/path/to/exported/file.csv",
  "message": "Results exported to CSV successfully"
}
```

**Export File Naming Convention:**
- Format: `{job_name}_{job_id}_{timestamp}.{extension}`
- Example: `product_scraping_12345_20240101_120000.csv`

**Example:**
```javascript
// Export to CSV
const csvExport = await eel.export_results("job-uuid-123", "csv")();

// Export to Excel
const xlsxExport = await eel.export_results("job-uuid-123", "xlsx")();

// Export to JSON
const jsonExport = await eel.export_results("job-uuid-123", "json")();
```

### CSV Export Format

CSV exports include all scraped fields as columns with proper escaping:

```csv
id,source_url,title,price,description,scraped_at,status
1,https://example.com/product1,"Product Name","29.99","Product description","2024-01-01T12:00:00Z","success"
2,https://example.com/product2,"Another Product","39.99","Another description","2024-01-01T12:01:00Z","success"
```

**CSV Features:**
- UTF-8 encoding
- Proper quote escaping
- Null value handling
- Nested object flattening

### JSON Export Format

JSON exports preserve original data structure:

```json
{
  "export_metadata": {
    "job_id": "job-uuid-123",
    "job_name": "Product Scraping",
    "export_date": "2024-01-01T15:30:00Z",
    "total_records": 150,
    "format": "json",
    "version": "1.0"
  },
  "results": [
    {
      "id": "result-uuid-1",
      "source_url": "https://example.com/product1",
      "data": {
        "title": "Product Name",
        "price": 29.99,
        "description": "Product description",
        "images": ["image1.jpg", "image2.jpg"],
        "attributes": {
          "color": "blue",
          "size": "large"
        }
      },
      "scraped_at": "2024-01-01T12:00:00Z",
      "status": "success"
    }
  ]
}
```

### Excel Export Format

Excel exports create structured spreadsheets with:

- **Data Sheet**: Main scraped data
- **Metadata Sheet**: Job information and statistics
- **Summary Sheet**: Data overview and counts

**Excel Features:**
- Multiple worksheets
- Formatted headers
- Data type preservation
- Automatic column sizing

### XML Export Format

XML exports provide hierarchical data structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<export>
  <metadata>
    <job_id>job-uuid-123</job_id>
    <job_name>Product Scraping</job_name>
    <export_date>2024-01-01T15:30:00Z</export_date>
    <total_records>150</total_records>
  </metadata>
  <results>
    <result id="result-uuid-1">
      <source_url>https://example.com/product1</source_url>
      <data>
        <title>Product Name</title>
        <price>29.99</price>
        <description>Product description</description>
        <images>
          <image>image1.jpg</image>
          <image>image2.jpg</image>
        </images>
      </data>
      <scraped_at>2024-01-01T12:00:00Z</scraped_at>
      <status>success</status>
    </result>
  </results>
</export>
```

## Data Processing

ScraperV4 includes built-in data processing capabilities through the DataService.

### Process Scraped Data

**Internal Function:** `process_scraped_data(data, processing_rules)`

Applies post-processing rules to scraped data before export.

**Processing Rule Types:**

#### Text Processing
- `strip`: Remove whitespace
- `lowercase`: Convert to lowercase  
- `uppercase`: Convert to uppercase
- `capitalize`: Capitalize first letter
- `trim`: Remove specific characters
- `replace`: Replace text patterns

#### Numeric Processing
- `extract_number`: Extract numeric values
- `parse_float`: Convert to decimal
- `parse_int`: Convert to integer
- `round`: Round decimal places
- `format_currency`: Format as currency

#### List Processing
- `unique`: Remove duplicates
- `flatten`: Flatten nested lists
- `sort`: Sort elements
- `filter`: Filter by criteria
- `limit`: Limit number of items

#### Validation Processing
- `validate_email`: Email format validation
- `validate_url`: URL format validation
- `validate_phone`: Phone number validation
- `validate_required`: Required field validation

**Example Processing Rules:**
```json
{
  "post_processing": [
    {
      "type": "strip",
      "field": "title"
    },
    {
      "type": "extract_number",
      "field": "price",
      "options": {
        "decimal_places": 2
      }
    },
    {
      "type": "validate_email",
      "field": "contact_email",
      "options": {
        "required": false,
        "default": null
      }
    },
    {
      "type": "unique",
      "field": "tags"
    }
  ]
}
```

### Data Cleaning

Automatic data cleaning includes:

**Null Value Handling:**
- Remove empty strings
- Convert "null", "N/A", "None" to null
- Handle missing data gracefully

**Data Type Conversion:**
- Automatic type inference
- String to number conversion
- Boolean value parsing
- Date/time parsing

**Duplicate Detection:**
- Row-level duplicate removal
- Field-level duplicate handling
- Configurable similarity thresholds

## Data Storage

### Result Storage Structure

ScraperV4 stores results in organized JSON files:

```
data/
├── jobs/
│   ├── job-uuid-123.json          # Job metadata
│   └── job-uuid-456.json
├── results/
│   ├── job-uuid-123/              # Job-specific results
│   │   ├── result-1.json
│   │   ├── result-2.json
│   │   └── metadata.json
│   └── job-uuid-456/
└── exports/
    ├── job-uuid-123_export.csv    # Exported files
    └── job-uuid-123_export.xlsx
```

### Result Metadata

Each result includes comprehensive metadata:

```json
{
  "id": "result-uuid-1",
  "job_id": "job-uuid-123",
  "source_url": "https://example.com/page",
  "data": {
    "title": "Scraped Title",
    "content": "Scraped content..."
  },
  "metadata": {
    "template_used": "blog_scraper",
    "fetch_method": "stealth",
    "response_time": 1.2,
    "status_code": 200,
    "retry_count": 0,
    "processing_time": 0.5
  },
  "scraped_at": "2024-01-01T12:00:00Z",
  "status": "success",
  "validation_results": {
    "required_fields_present": true,
    "type_validation_passed": true,
    "custom_validation_passed": true
  }
}
```

## Data Retrieval

### Get Job Results with Filtering

While not exposed directly via Eel, the DataService provides advanced filtering:

**Filter Options:**
- **Date Range**: Filter by scraping date
- **Status**: Filter by success/failure status
- **URL Pattern**: Filter by source URL patterns
- **Data Content**: Filter by data field values
- **Template**: Filter by template used

**Sorting Options:**
- **Chronological**: By scraping timestamp
- **Alphabetical**: By URL or data fields
- **Status**: Success first or failures first
- **Custom**: User-defined sorting rules

**Pagination Options:**
- **Limit**: Maximum results per page
- **Offset**: Starting position
- **Cursor**: Cursor-based pagination
- **Total Count**: Include total result count

### Data Statistics

The DataService automatically calculates statistics:

```json
{
  "total_items": 1500,
  "successful_items": 1425,
  "failed_items": 75,
  "success_rate": 95.0,
  "average_response_time": 1.8,
  "data_size": "2.5 MB",
  "field_coverage": {
    "title": 100.0,
    "price": 95.2,
    "description": 87.5,
    "images": 78.3
  },
  "source_domains": {
    "example.com": 800,
    "store.com": 700
  }
}
```

## Error Handling

Data operations return consistent error responses:

```json
{
  "success": false,
  "error": "Descriptive error message",
  "error_code": "DATA_EXPORT_001",
  "details": {
    "job_id": "job-uuid-123",
    "format": "csv",
    "attempted_at": "2024-01-01T12:00:00Z"
  }
}
```

**Common Data Errors:**
- `DATA_EXPORT_001`: Export format not supported
- `DATA_EXPORT_002`: Job results not found
- `DATA_EXPORT_003`: Export file creation failed
- `DATA_PROCESS_001`: Processing rule invalid
- `DATA_PROCESS_002`: Data validation failed
- `DATA_STORAGE_001`: Storage write failed
- `DATA_RETRIEVAL_001`: Results not accessible

## File Management

### Export File Cleanup

ScraperV4 automatically manages export files:

**Cleanup Policies:**
- Files older than 30 days are automatically deleted
- Maximum 100 export files per job
- Large files (>100MB) are compressed
- Failed exports are cleaned up immediately

**Manual Cleanup:**
```javascript
// Note: This would need to be implemented as a separate endpoint
const cleanup = await eel.cleanup_export_files(job_id)();
```

### Storage Quotas

**Default Limits:**
- Maximum 1GB per job results
- Maximum 100MB per individual result
- Maximum 10,000 results per job
- Maximum 1 year data retention

## Performance Optimization

### Streaming Exports

For large datasets, ScraperV4 supports streaming exports:

- **Memory Efficient**: Process data in chunks
- **Progress Tracking**: Real-time export progress
- **Cancellation**: Ability to cancel long exports
- **Resume**: Resume interrupted exports

### Compression

Automatic compression for large exports:

- **ZIP**: Multiple file exports
- **GZIP**: Single file compression
- **BZIP2**: High compression ratio
- **Auto**: Automatic format selection

## See Also

- [Job Results API](scraping-endpoints.md#get-job-results) - Retrieving raw results
- [Data Models](../classes/models.md) - Data structure documentation
- [Services Reference](../classes/services.md) - DataService class documentation
- [Configuration](../configuration/environment-variables.md) - Storage and export settings