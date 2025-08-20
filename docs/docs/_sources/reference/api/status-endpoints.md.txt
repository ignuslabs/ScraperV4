# Status Endpoints Reference

This document provides complete reference for all status monitoring and health check API endpoints in ScraperV4.

## Health Checks

### System Health Check

**Function:** `ping()`

Basic health check to verify that the ScraperV4 backend is running and responsive.

**Parameters:** None

**Returns:**
```json
{
  "status": "ok",
  "message": "ScraperV4 backend is running"
}
```

**Response Codes:**
- `ok`: System is healthy and responsive
- `degraded`: System is running but with performance issues
- `error`: System is experiencing problems

**Example:**
```javascript
const health = await eel.ping()();
if (health.status === "ok") {
  console.log("Backend is healthy");
}
```

### Detailed System Status

**Function:** `get_system_status()` *(Internal)*

Comprehensive system health and performance metrics.

**Returns:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T12:00:00Z",
  "uptime": 86400,
  "version": "1.0.0",
  "components": {
    "job_manager": {
      "status": "ok",
      "active_jobs": 3,
      "total_jobs": 157,
      "memory_usage": "45.2 MB"
    },
    "template_manager": {
      "status": "ok",
      "loaded_templates": 12,
      "total_templates": 15,
      "cache_hit_rate": 95.2
    },
    "data_service": {
      "status": "ok",
      "storage_used": "2.1 GB",
      "storage_available": "7.9 GB",
      "io_operations": 1250
    },
    "scraping_service": {
      "status": "ok",
      "active_scrapers": 5,
      "requests_per_minute": 45,
      "success_rate": 94.5
    }
  },
  "performance": {
    "cpu_usage": 23.5,
    "memory_usage": 67.8,
    "disk_usage": 21.0,
    "network_latency": 1.2
  }
}
```

## Application Settings

### Get Application Settings

**Function:** `get_settings()`

Retrieves current application configuration settings.

**Parameters:** None

**Returns:**
```json
{
  "success": true,
  "settings": {
    "default_delay": 2.0,
    "max_retries": 3,
    "timeout": 30,
    "stealth_mode": true,
    "concurrent_jobs": 3
  }
}
```

**Setting Descriptions:**
- `default_delay`: Default delay between requests (seconds)
- `max_retries`: Maximum retry attempts for failed requests
- `timeout`: Request timeout duration (seconds)
- `stealth_mode`: Enable stealth browsing features
- `concurrent_jobs`: Maximum number of simultaneous jobs

**Example:**
```javascript
const settings = await eel.get_settings()();
if (settings.success) {
  console.log(`Delay: ${settings.settings.default_delay}s`);
  console.log(`Concurrent jobs: ${settings.settings.concurrent_jobs}`);
}
```

### Update Application Settings

**Function:** `update_settings(settings)`

Updates application configuration settings.

**Parameters:**
- `settings` (Dict[str, Any]): Settings to update
  - `default_delay` (float): Request delay in seconds
  - `max_retries` (int): Maximum retry attempts
  - `timeout` (int): Request timeout in seconds
  - `stealth_mode` (bool): Enable/disable stealth mode
  - `concurrent_jobs` (int): Maximum concurrent jobs

**Setting Constraints:**
- `default_delay`: 0.1 - 60.0 seconds
- `max_retries`: 0 - 10 attempts
- `timeout`: 5 - 300 seconds
- `concurrent_jobs`: 1 - 10 jobs

**Returns:**
```json
{
  "success": true,
  "message": "Settings updated successfully"
}
```

**Example:**
```javascript
const newSettings = {
  default_delay: 1.5,
  max_retries: 5,
  stealth_mode: true,
  concurrent_jobs: 5
};

const result = await eel.update_settings(newSettings)();
if (result.success) {
  console.log("Settings updated successfully");
}
```

## Job Monitoring

### Active Jobs Overview

**Function:** `get_active_jobs()` *(Internal)*

Retrieves information about all currently active jobs.

**Returns:**
```json
{
  "success": true,
  "active_jobs": [
    {
      "id": "job-uuid-123",
      "name": "Product Scraping",
      "status": "running",
      "progress": 45,
      "started_at": "2024-01-01T12:00:00Z",
      "estimated_completion": "2024-01-01T12:30:00Z",
      "items_scraped": 120,
      "items_failed": 5,
      "current_url": "https://example.com/page-45"
    }
  ],
  "total_active": 3,
  "queue_length": 7
}
```

### Job Statistics

**Function:** `get_job_statistics()` *(Internal)*

Comprehensive statistics across all jobs.

**Returns:**
```json
{
  "success": true,
  "statistics": {
    "total_jobs": 1250,
    "completed_jobs": 1187,
    "failed_jobs": 43,
    "stopped_jobs": 20,
    "success_rate": 94.96,
    "average_duration": 285.5,
    "total_items_scraped": 156789,
    "total_items_failed": 4231,
    "popular_templates": [
      {
        "name": "product_scraper",
        "usage_count": 450,
        "success_rate": 96.2
      },
      {
        "name": "blog_scraper", 
        "usage_count": 320,
        "success_rate": 92.8
      }
    ],
    "daily_stats": [
      {
        "date": "2024-01-01",
        "jobs_completed": 45,
        "items_scraped": 2341,
        "success_rate": 95.5
      }
    ]
  }
}
```

## Performance Monitoring

### Resource Usage

**Function:** `get_resource_usage()` *(Internal)*

Current system resource utilization.

**Returns:**
```json
{
  "success": true,
  "resources": {
    "cpu": {
      "current_usage": 23.5,
      "average_usage": 18.7,
      "peak_usage": 89.2,
      "core_count": 8
    },
    "memory": {
      "current_usage": 512.3,
      "total_available": 2048.0,
      "usage_percentage": 25.0,
      "peak_usage": 1024.5
    },
    "disk": {
      "data_usage": 2.1,
      "logs_usage": 0.3,
      "exports_usage": 0.8,
      "total_usage": 3.2,
      "available_space": 27.8
    },
    "network": {
      "requests_per_minute": 45,
      "bytes_downloaded": 1024000,
      "bytes_uploaded": 256000,
      "active_connections": 12,
      "average_latency": 1.2
    }
  }
}
```

### Performance Metrics

**Function:** `get_performance_metrics()` *(Internal)*

Detailed performance metrics and benchmarks.

**Returns:**
```json
{
  "success": true,
  "metrics": {
    "scraping_performance": {
      "average_page_load_time": 2.1,
      "average_extraction_time": 0.3,
      "requests_per_second": 0.8,
      "cache_hit_rate": 78.5,
      "retry_rate": 4.2
    },
    "system_performance": {
      "response_times": {
        "api_calls": {
          "average": 0.15,
          "p95": 0.45,
          "p99": 1.2
        },
        "template_loading": {
          "average": 0.08,
          "p95": 0.25,
          "p99": 0.8
        }
      },
      "throughput": {
        "jobs_per_hour": 85,
        "items_per_hour": 3240,
        "data_processed": "156 MB/hour"
      }
    },
    "error_rates": {
      "http_errors": 2.1,
      "parsing_errors": 0.8,
      "timeout_errors": 1.2,
      "validation_errors": 0.5
    }
  }
}
```

## Error Monitoring

### Error Statistics

**Function:** `get_error_statistics()` *(Internal)*

Comprehensive error tracking and analysis.

**Returns:**
```json
{
  "success": true,
  "errors": {
    "total_errors": 127,
    "error_rate": 2.4,
    "categories": {
      "network_errors": {
        "count": 45,
        "percentage": 35.4,
        "common_causes": [
          "Connection timeout",
          "DNS resolution failed", 
          "SSL certificate invalid"
        ]
      },
      "parsing_errors": {
        "count": 32,
        "percentage": 25.2,
        "common_causes": [
          "Selector not found",
          "Invalid HTML structure",
          "JavaScript required"
        ]
      },
      "validation_errors": {
        "count": 28,
        "percentage": 22.0,
        "common_causes": [
          "Required field missing",
          "Invalid data type",
          "Validation rule failed"
        ]
      },
      "system_errors": {
        "count": 22,
        "percentage": 17.3,
        "common_causes": [
          "Memory limit exceeded",
          "Disk space full",
          "Process crashed"
        ]
      }
    },
    "recent_errors": [
      {
        "timestamp": "2024-01-01T12:30:00Z",
        "job_id": "job-uuid-123",
        "error_type": "network_error",
        "message": "Connection timeout after 30 seconds",
        "url": "https://example.com/slow-page"
      }
    ]
  }
}
```

## Logging and Monitoring

### Frontend Activity Logging

**Function:** `log_frontend_activity(logs)`

Logs frontend activity to backend for centralized monitoring.

**Parameters:**
- `logs` (List[Dict[str, Any]]): Array of log entries
  - `level` (str): Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
  - `component` (str): Frontend component name
  - `message` (str): Log message
  - `data` (Any, optional): Additional log data
  - `timestamp` (str): ISO timestamp

**Returns:**
```json
{
  "success": true,
  "logged": 5
}
```

**Log Levels:**
- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Warning conditions that should be noted
- `ERROR`: Error conditions that need attention
- `CRITICAL`: Critical errors requiring immediate action

**Example:**
```javascript
const logs = [
  {
    level: "INFO",
    component: "ScrapingForm",
    message: "User started new scraping job",
    data: {
      template: "product_scraper",
      url: "https://example.com"
    },
    timestamp: new Date().toISOString()
  },
  {
    level: "WARNING",
    component: "TemplateManager",
    message: "Template validation warning",
    data: {
      template_id: "blog_scraper",
      warnings: ["Selector might be unstable"]
    },
    timestamp: new Date().toISOString()
  }
];

const result = await eel.log_frontend_activity(logs)();
```

### Log File Access

**Log Files Location:**
- `logs/scraperv4.log`: Main backend logs
- `logs/frontend.log`: Frontend activity logs  
- `logs/error.log`: Error-specific logs
- `logs/performance.log`: Performance metrics

**Log Rotation:**
- Maximum file size: 10MB
- Backup count: 5 files
- Automatic compression: Yes
- Retention period: 30 days

## Real-time Updates

### Progress Broadcasting

ScraperV4 provides real-time status updates via Eel's broadcasting system.

**Progress Update Format:**
```json
{
  "type": "job_progress",
  "job_id": "job-uuid-123",
  "progress": 65,
  "items_scraped": 195,
  "items_failed": 8,
  "current_url": "https://example.com/page-65",
  "timestamp": "2024-01-01T12:15:30Z"
}
```

**System Status Updates:**
```json
{
  "type": "system_status",
  "status": "healthy",
  "active_jobs": 4,
  "cpu_usage": 34.2,
  "memory_usage": 56.8,
  "timestamp": "2024-01-01T12:15:30Z"
}
```

**Error Notifications:**
```json
{
  "type": "error_notification",
  "severity": "warning",
  "message": "High memory usage detected",
  "details": {
    "current_usage": 85.2,
    "threshold": 80.0
  },
  "timestamp": "2024-01-01T12:15:30Z"
}
```

### Status Subscription

**JavaScript Event Handling:**
```javascript
// Subscribe to all status updates
eel.expose(handleStatusUpdate);
function handleStatusUpdate(statusData) {
  switch(statusData.type) {
    case 'job_progress':
      updateJobProgress(statusData);
      break;
    case 'system_status':
      updateSystemStatus(statusData);
      break;
    case 'error_notification':
      showErrorNotification(statusData);
      break;
  }
}
```

## Error Handling

Status endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Descriptive error message",
  "error_code": "STATUS_001",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Common Status Errors:**
- `STATUS_001`: System health check failed
- `STATUS_002`: Settings update failed
- `STATUS_003`: Invalid setting value
- `STATUS_004`: Performance metrics unavailable
- `STATUS_005`: Log access denied

## See Also

- [Scraping Endpoints](scraping-endpoints.md) - Job management and execution
- [Configuration Reference](../configuration/environment-variables.md) - System settings
- [Error Handling](../error-handling.md) - Complete error reference
- [Services Reference](../classes/services.md) - Service class documentation