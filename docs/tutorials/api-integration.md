# API Integration Tutorial

This comprehensive tutorial covers using ScraperV4's REST API for programmatic control, automation, and integration with other systems. You'll learn to build client applications, automate scraping workflows, and integrate ScraperV4 into larger data pipelines.

## Learning Objectives

By completing this tutorial, you will:
- Master the complete ScraperV4 REST API
- Build client applications in multiple programming languages
- Implement automated scraping workflows
- Integrate with databases and data processing systems
- Handle authentication and error scenarios
- Monitor and manage large-scale operations programmatically

## Prerequisites

- Completed previous ScraperV4 tutorials
- Basic understanding of REST APIs and HTTP protocols
- Programming knowledge (Python, JavaScript, or similar)
- ScraperV4 running with API access enabled

## API Overview

### Core Endpoint Categories

ScraperV4 provides several API endpoint groups:

1. **Scraping Operations** (`/api/scraping/*`) - Job management and execution
2. **Template Management** (`/api/templates/*`) - Template CRUD operations  
3. **Data Operations** (`/api/data/*`) - Result retrieval and export
4. **System Management** (`/api/system/*`) - Status and configuration
5. **Monitoring** (`/api/monitoring/*`) - Performance and health metrics

### Base URL and Authentication

```
Base URL: http://localhost:8080/api
Content-Type: application/json
Authentication: API Key (optional, if configured)
```

## Part 1: Authentication and Setup

### 1.1 API Key Configuration (Optional)

If you want to secure your API, configure authentication:

```python
# In your ScraperV4 configuration
api_config = {
    "authentication": {
        "enabled": True,
        "method": "api_key",
        "api_keys": [
            {"key": "sk-scraperv4-your-secret-key", "name": "primary"},
            {"key": "sk-scraperv4-backup-key", "name": "backup"}
        ]
    }
}
```

### 1.2 Client Setup Examples

**Python Client Setup**:
```python
import requests
import json
from typing import Dict, List, Optional

class ScraperV4Client:
    def __init__(self, base_url: str = "http://localhost:8080/api", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        
        self.session.headers.update({"Content-Type": "application/json"})
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response
```

**JavaScript Client Setup**:
```javascript
class ScraperV4Client {
    constructor(baseUrl = 'http://localhost:8080/api', apiKey = null) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.apiKey = apiKey;
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
        
        if (apiKey) {
            this.defaultHeaders['Authorization'] = `Bearer ${apiKey}`;
        }
    }
    
    async request(method, endpoint, data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            method,
            headers: this.defaultHeaders
        };
        
        if (data) {
            config.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response.json();
    }
}
```

## Part 2: Template Management API

### 2.1 Creating Templates Programmatically

**Create a New Template**:
```python
def create_template(client: ScraperV4Client):
    template_data = {
        "name": "E-commerce Product API Template",
        "description": "Scrapes product information from e-commerce sites",
        "version": "1.0",
        "selectors": {
            "title": "h1.product-title::text",
            "price": ".price-current::text",
            "description": ".product-description::text",
            "images": "img.product-image::attr(src)",
            "rating": ".rating-stars::attr(data-rating)",
            "reviews_count": ".reviews-count::text"
        },
        "post_processing": {
            "clean_text": True,
            "extract_numbers": ["price", "rating"],
            "normalize_urls": ["images"]
        },
        "pagination": {
            "enabled": True,
            "next_page_selector": ".pagination .next",
            "max_pages": 50
        }
    }
    
    response = client._request('POST', '/templates', json=template_data)
    template_id = response.json()['template_id']
    print(f"Created template with ID: {template_id}")
    return template_id

# Usage
client = ScraperV4Client()
template_id = create_template(client)
```

### 2.2 Template Testing API

**Test Template Against URL**:
```python
def test_template(client: ScraperV4Client, template_id: str, test_url: str):
    test_data = {
        "template_id": template_id,
        "test_url": test_url,
        "options": {
            "return_html": False,
            "include_metadata": True,
            "validate_selectors": True
        }
    }
    
    response = client._request('POST', f'/templates/{template_id}/test', json=test_data)
    result = response.json()
    
    print("Test Results:")
    print(f"Success: {result['success']}")
    print(f"Extracted Data: {json.dumps(result['data'], indent=2)}")
    
    if result.get('validation_errors'):
        print(f"Validation Errors: {result['validation_errors']}")
    
    return result

# Usage
test_result = test_template(client, template_id, "https://example-shop.com/product/123")
```

### 2.3 Template Management Operations

**List All Templates**:
```python
def list_templates(client: ScraperV4Client, filters: Optional[Dict] = None):
    params = filters or {}
    response = client._request('GET', '/templates', params=params)
    templates = response.json()['templates']
    
    print(f"Found {len(templates)} templates:")
    for template in templates:
        print(f"- {template['name']} (ID: {template['id']}, Version: {template['version']})")
    
    return templates

# Usage with filters
templates = list_templates(client, {"category": "e-commerce", "status": "active"})
```

**Update Existing Template**:
```python
def update_template(client: ScraperV4Client, template_id: str, updates: Dict):
    response = client._request('PUT', f'/templates/{template_id}', json=updates)
    result = response.json()
    print(f"Template updated: {result['message']}")
    return result

# Usage
updates = {
    "selectors": {
        "title": "h1.product-title::text, .item-title::text",  # Added fallback
        "availability": ".stock-status::text"  # New field
    },
    "version": "1.1"
}
update_template(client, template_id, updates)
```

## Part 3: Scraping Operations API

### 3.1 Creating and Managing Jobs

**Start a Scraping Job**:
```python
def start_scraping_job(client: ScraperV4Client, job_config: Dict):
    response = client._request('POST', '/scraping/start', json=job_config)
    job_data = response.json()
    
    job_id = job_data['job_id']
    print(f"Started scraping job: {job_id}")
    print(f"Status: {job_data['status']}")
    
    return job_id

# Advanced job configuration
job_config = {
    "name": "Product Catalog Scrape - API",
    "template_id": template_id,
    "target_url": "https://example-shop.com/products",
    "options": {
        "use_proxy": True,
        "proxy_strategy": "performance",
        "stealth_mode": "high",
        "max_pages": 100,
        "delay_range": [2, 5],
        "retry_attempts": 3,
        "enable_anti_bot_detection": True,
        "export_format": "json",
        "include_metadata": True
    },
    "scheduling": {
        "start_immediately": True,
        "priority": "high"
    }
}

job_id = start_scraping_job(client, job_config)
```

### 3.2 Real-time Job Monitoring

**Monitor Job Progress**:
```python
import time
from typing import Callable

def monitor_job_progress(
    client: ScraperV4Client, 
    job_id: str, 
    update_callback: Optional[Callable] = None,
    poll_interval: int = 5
):
    """Monitor job progress with real-time updates"""
    
    while True:
        response = client._request('GET', f'/scraping/status/{job_id}')
        status = response.json()
        
        print(f"\rJob {job_id}: {status['status']} - "
              f"{status['progress']:.1f}% - "
              f"{status['items_scraped']} items", end='')
        
        if update_callback:
            update_callback(status)
        
        if status['status'] in ['completed', 'failed', 'cancelled']:
            print(f"\nJob finished with status: {status['status']}")
            break
        
        time.sleep(poll_interval)
    
    return status

# Usage with custom callback
def progress_callback(status):
    if status['status'] == 'running':
        eta = status.get('estimated_completion', 'Unknown')
        print(f" (ETA: {eta})")

final_status = monitor_job_progress(client, job_id, progress_callback)
```

### 3.3 Job Control Operations

**Pause, Resume, and Cancel Jobs**:
```python
def control_job(client: ScraperV4Client, job_id: str, action: str):
    """Control job execution (pause, resume, cancel)"""
    
    valid_actions = ['pause', 'resume', 'cancel']
    if action not in valid_actions:
        raise ValueError(f"Invalid action. Must be one of: {valid_actions}")
    
    response = client._request('POST', f'/scraping/{action}/{job_id}')
    result = response.json()
    
    print(f"Job {job_id} {action} result: {result['message']}")
    return result

# Usage examples
# control_job(client, job_id, 'pause')
# control_job(client, job_id, 'resume')
# control_job(client, job_id, 'cancel')
```

## Part 4: Data Retrieval and Export API

### 4.1 Retrieving Scraped Data

**Get Job Results**:
```python
def get_job_results(
    client: ScraperV4Client, 
    job_id: str, 
    format: str = 'json',
    filters: Optional[Dict] = None
):
    """Retrieve scraped data from a completed job"""
    
    params = {'format': format}
    if filters:
        params.update(filters)
    
    response = client._request('GET', f'/data/results/{job_id}', params=params)
    
    if format == 'json':
        return response.json()
    else:
        return response.content  # For CSV, Excel formats

# Usage
results = get_job_results(client, job_id, format='json')
print(f"Retrieved {len(results['data'])} items")

# With filters
filtered_results = get_job_results(
    client, 
    job_id, 
    filters={
        'min_price': 50,
        'category': 'electronics',
        'limit': 100
    }
)
```

### 4.2 Advanced Data Export

**Export with Custom Options**:
```python
def export_job_data(client: ScraperV4Client, job_id: str, export_config: Dict):
    """Export data with advanced formatting options"""
    
    response = client._request('POST', '/data/export', json={
        'job_id': job_id,
        **export_config
    })
    
    export_info = response.json()
    download_url = export_info['download_url']
    
    # Download the exported file
    file_response = client._request('GET', download_url)
    
    filename = export_info['filename']
    with open(filename, 'wb') as f:
        f.write(file_response.content)
    
    print(f"Exported data to: {filename}")
    return filename

# Advanced export configuration
export_config = {
    "format": "xlsx",
    "options": {
        "include_metadata": True,
        "separate_sheets": True,
        "apply_formatting": True,
        "filter_empty_rows": True,
        "add_charts": True
    },
    "processing": {
        "deduplicate": True,
        "sort_by": "price",
        "group_by": "category"
    }
}

exported_file = export_job_data(client, job_id, export_config)
```

### 4.3 Streaming Large Datasets

**Stream Large Results**:
```python
def stream_job_results(client: ScraperV4Client, job_id: str, chunk_size: int = 1000):
    """Stream large datasets in chunks"""
    
    offset = 0
    total_items = None
    
    while True:
        params = {
            'offset': offset,
            'limit': chunk_size,
            'include_total': True if offset == 0 else False
        }
        
        response = client._request('GET', f'/data/results/{job_id}', params=params)
        chunk_data = response.json()
        
        if offset == 0:
            total_items = chunk_data['total_items']
            print(f"Streaming {total_items} total items...")
        
        items = chunk_data['data']
        if not items:
            break
        
        # Process chunk
        for item in items:
            yield item
        
        offset += len(items)
        print(f"Processed {offset}/{total_items} items...")
        
        if len(items) < chunk_size:
            break

# Usage
for item in stream_job_results(client, job_id):
    # Process each item individually
    process_item(item)
```

## Part 5: Batch Operations and Automation

### 5.1 Batch Job Management

**Create Multiple Jobs**:
```python
def create_batch_jobs(client: ScraperV4Client, job_configs: List[Dict]):
    """Create multiple jobs in batch"""
    
    batch_request = {
        "jobs": job_configs,
        "options": {
            "start_immediately": False,
            "priority": "normal",
            "max_concurrent": 3
        }
    }
    
    response = client._request('POST', '/scraping/batch', json=batch_request)
    batch_info = response.json()
    
    job_ids = batch_info['job_ids']
    print(f"Created {len(job_ids)} jobs in batch")
    
    return job_ids

# Create jobs for multiple product categories
categories = ['electronics', 'clothing', 'books', 'home-garden']
job_configs = []

for category in categories:
    job_configs.append({
        "name": f"Products - {category.title()}",
        "template_id": template_id,
        "target_url": f"https://example-shop.com/category/{category}",
        "options": {
            "stealth_mode": "medium",
            "max_pages": 20
        }
    })

batch_job_ids = create_batch_jobs(client, job_configs)
```

### 5.2 Automated Workflows

**Create Automated Scraping Pipeline**:
```python
class ScrapingPipeline:
    def __init__(self, client: ScraperV4Client):
        self.client = client
        self.job_queue = []
        self.completed_jobs = []
        self.failed_jobs = []
    
    def add_job(self, job_config: Dict):
        """Add job to pipeline"""
        self.job_queue.append(job_config)
    
    def execute_pipeline(self, max_concurrent: int = 3):
        """Execute all jobs in pipeline with concurrency control"""
        import concurrent.futures
        import threading
        
        def execute_job(job_config):
            try:
                job_id = start_scraping_job(self.client, job_config)
                final_status = monitor_job_progress(self.client, job_id)
                
                if final_status['status'] == 'completed':
                    self.completed_jobs.append(job_id)
                    return {'job_id': job_id, 'status': 'success', 'data': final_status}
                else:
                    self.failed_jobs.append(job_id)
                    return {'job_id': job_id, 'status': 'failed', 'data': final_status}
                    
            except Exception as e:
                return {'job_id': None, 'status': 'error', 'error': str(e)}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = [executor.submit(execute_job, job) for job in self.job_queue]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                print(f"Job completed: {result}")
        
        print(f"Pipeline completed: {len(self.completed_jobs)} successful, {len(self.failed_jobs)} failed")

# Usage
pipeline = ScrapingPipeline(client)

# Add multiple jobs to pipeline
websites = [
    {"name": "Site A Products", "url": "https://site-a.com/products", "template": "template_a"},
    {"name": "Site B Products", "url": "https://site-b.com/items", "template": "template_b"},
    {"name": "Site C Catalog", "url": "https://site-c.com/catalog", "template": "template_c"}
]

for site in websites:
    pipeline.add_job({
        "name": site["name"],
        "template_id": site["template"],
        "target_url": site["url"],
        "options": {"stealth_mode": "high", "max_pages": 10}
    })

# Execute pipeline
pipeline.execute_pipeline(max_concurrent=2)
```

## Part 6: Integration with Databases

### 6.1 Database Integration

**Save Results to Database**:
```python
import sqlite3
import pandas as pd
from typing import Any

class DatabaseIntegration:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS scraping_jobs (
                    job_id TEXT PRIMARY KEY,
                    job_name TEXT,
                    template_id TEXT,
                    target_url TEXT,
                    status TEXT,
                    created_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    items_count INTEGER
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS scraped_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT,
                    item_data JSON,
                    scraped_at TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES scraping_jobs (job_id)
                )
            ''')
    
    def save_job_metadata(self, job_info: Dict):
        """Save job metadata to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO scraping_jobs 
                (job_id, job_name, template_id, target_url, status, created_at, completed_at, items_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_info['job_id'],
                job_info['name'],
                job_info['template_id'],
                job_info['target_url'],
                job_info['status'],
                job_info['created_at'],
                job_info.get('completed_at'),
                job_info.get('items_count', 0)
            ))
    
    def save_scraped_data(self, job_id: str, items: List[Dict]):
        """Save scraped items to database"""
        with sqlite3.connect(self.db_path) as conn:
            for item in items:
                conn.execute('''
                    INSERT INTO scraped_data (job_id, item_data, scraped_at)
                    VALUES (?, ?, datetime('now'))
                ''', (job_id, json.dumps(item)))
    
    def get_job_summary(self) -> pd.DataFrame:
        """Get summary of all scraping jobs"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query('''
                SELECT 
                    job_name,
                    status,
                    items_count,
                    created_at,
                    completed_at,
                    (julianday(completed_at) - julianday(created_at)) * 24 * 60 as duration_minutes
                FROM scraping_jobs
                ORDER BY created_at DESC
            ''', conn)

# Integration example
def automated_scraping_with_database(client: ScraperV4Client, db_integration: DatabaseIntegration):
    """Complete workflow with database integration"""
    
    # Start job
    job_config = {
        "name": "Daily Product Update",
        "template_id": template_id,
        "target_url": "https://example-shop.com/new-products",
        "options": {"stealth_mode": "medium", "max_pages": 5}
    }
    
    job_id = start_scraping_job(client, job_config)
    
    # Save initial job metadata
    db_integration.save_job_metadata({
        'job_id': job_id,
        'name': job_config['name'],
        'template_id': job_config['template_id'],
        'target_url': job_config['target_url'],
        'status': 'running',
        'created_at': datetime.now().isoformat()
    })
    
    # Monitor and update
    final_status = monitor_job_progress(client, job_id)
    
    # Get results and save to database
    if final_status['status'] == 'completed':
        results = get_job_results(client, job_id)
        db_integration.save_scraped_data(job_id, results['data'])
        
        # Update job metadata
        db_integration.save_job_metadata({
            'job_id': job_id,
            'name': job_config['name'],
            'template_id': job_config['template_id'],
            'target_url': job_config['target_url'],
            'status': 'completed',
            'created_at': final_status['created_at'],
            'completed_at': datetime.now().isoformat(),
            'items_count': len(results['data'])
        })

# Usage
db_integration = DatabaseIntegration("scraping_data.db")
automated_scraping_with_database(client, db_integration)

# View summary
summary = db_integration.get_job_summary()
print(summary)
```

## Part 7: Real-time Notifications and Webhooks

### 7.1 Webhook Configuration

**Setup Webhook Notifications**:
```python
def configure_webhooks(client: ScraperV4Client, webhook_config: Dict):
    """Configure webhook notifications for job events"""
    
    response = client._request('POST', '/system/webhooks', json=webhook_config)
    webhook_id = response.json()['webhook_id']
    
    print(f"Configured webhook: {webhook_id}")
    return webhook_id

# Webhook configuration
webhook_config = {
    "url": "https://your-server.com/webhooks/scraperv4",
    "events": [
        "job_started",
        "job_completed", 
        "job_failed",
        "job_progress",  # Every 10% progress
        "error_occurred"
    ],
    "authentication": {
        "type": "bearer_token",
        "token": "your-webhook-secret"
    },
    "retry_policy": {
        "max_attempts": 3,
        "backoff_strategy": "exponential"
    }
}

webhook_id = configure_webhooks(client, webhook_config)
```

### 7.2 Webhook Handler Example

**Flask Webhook Handler**:
```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)

@app.route('/webhooks/scraperv4', methods=['POST'])
def handle_scraperv4_webhook():
    """Handle incoming webhook from ScraperV4"""
    
    # Verify webhook signature (if configured)
    signature = request.headers.get('X-ScraperV4-Signature')
    if signature:
        expected_signature = hmac.new(
            webhook_secret.encode(),
            request.data,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return jsonify({'error': 'Invalid signature'}), 401
    
    # Process webhook data
    webhook_data = request.json
    event_type = webhook_data['event_type']
    job_data = webhook_data['data']
    
    if event_type == 'job_completed':
        handle_job_completed(job_data)
    elif event_type == 'job_failed':
        handle_job_failed(job_data)
    elif event_type == 'job_progress':
        handle_job_progress(job_data)
    
    return jsonify({'status': 'received'})

def handle_job_completed(job_data):
    """Handle job completion"""
    job_id = job_data['job_id']
    print(f"Job {job_id} completed with {job_data['items_scraped']} items")
    
    # Trigger downstream processing
    process_completed_job(job_id)

def handle_job_failed(job_data):
    """Handle job failure"""
    job_id = job_data['job_id']
    error = job_data['error']
    print(f"Job {job_id} failed: {error}")
    
    # Send alert notification
    send_failure_alert(job_id, error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## Part 8: Monitoring and Analytics API

### 8.1 System Monitoring

**Get System Status**:
```python
def get_system_status(client: ScraperV4Client):
    """Get comprehensive system status"""
    
    response = client._request('GET', '/monitoring/status')
    status = response.json()
    
    print("System Status:")
    print(f"- Status: {status['status']}")
    print(f"- Active Jobs: {status['active_jobs']}")
    print(f"- Queue Size: {status['queue_size']}")
    print(f"- CPU Usage: {status['cpu_usage']:.1f}%")
    print(f"- Memory Usage: {status['memory_usage']:.1f}%")
    print(f"- Disk Usage: {status['disk_usage']:.1f}%")
    
    return status

def get_performance_metrics(client: ScraperV4Client, time_range: str = '24h'):
    """Get performance metrics over time"""
    
    params = {'time_range': time_range}
    response = client._request('GET', '/monitoring/metrics', params=params)
    metrics = response.json()
    
    print(f"Performance Metrics ({time_range}):")
    print(f"- Jobs Completed: {metrics['jobs_completed']}")
    print(f"- Success Rate: {metrics['success_rate']:.2%}")
    print(f"- Average Duration: {metrics['avg_duration']:.1f} minutes")
    print(f"- Items Per Hour: {metrics['items_per_hour']:.0f}")
    
    return metrics

# Usage
system_status = get_system_status(client)
performance_metrics = get_performance_metrics(client, '7d')
```

## Part 9: Error Handling and Debugging

### 9.1 Comprehensive Error Handling

**Robust API Client with Error Handling**:
```python
import time
import logging
from typing import Optional
from requests.exceptions import RequestException, HTTPError, Timeout

class RobustScraperV4Client(ScraperV4Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.retry_config = {
            'max_attempts': 3,
            'backoff_factor': 2,
            'retry_status_codes': [429, 500, 502, 503, 504]
        }
    
    def _request_with_retry(self, method: str, endpoint: str, **kwargs):
        """Make request with automatic retry logic"""
        
        last_exception = None
        
        for attempt in range(self.retry_config['max_attempts']):
            try:
                response = self._request(method, endpoint, **kwargs)
                return response
                
            except HTTPError as e:
                if e.response.status_code in self.retry_config['retry_status_codes']:
                    wait_time = self.retry_config['backoff_factor'] ** attempt
                    self.logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    last_exception = e
                    continue
                else:
                    # Don't retry for client errors (4xx except 429)
                    raise
                    
            except (RequestException, Timeout) as e:
                wait_time = self.retry_config['backoff_factor'] ** attempt
                self.logger.warning(f"Network error (attempt {attempt + 1}), retrying in {wait_time}s...")
                time.sleep(wait_time)
                last_exception = e
                continue
        
        # If we've exhausted all retries, raise the last exception
        raise last_exception
    
    def handle_api_error(self, error: Exception, context: str = ""):
        """Centralized error handling with context"""
        
        if isinstance(error, HTTPError):
            status_code = error.response.status_code
            
            if status_code == 400:
                self.logger.error(f"Bad request {context}: {error.response.text}")
            elif status_code == 401:
                self.logger.error(f"Authentication failed {context}")
            elif status_code == 403:
                self.logger.error(f"Access forbidden {context}")
            elif status_code == 404:
                self.logger.error(f"Resource not found {context}")
            elif status_code == 429:
                self.logger.warning(f"Rate limited {context}")
            elif status_code >= 500:
                self.logger.error(f"Server error {context}: {error.response.text}")
        
        elif isinstance(error, Timeout):
            self.logger.error(f"Request timeout {context}")
        
        elif isinstance(error, RequestException):
            self.logger.error(f"Network error {context}: {str(error)}")
        
        else:
            self.logger.error(f"Unexpected error {context}: {str(error)}")

# Usage with error handling
def safe_job_execution(client: RobustScraperV4Client, job_config: Dict):
    """Execute job with comprehensive error handling"""
    
    try:
        # Start job
        job_id = start_scraping_job(client, job_config)
        
        # Monitor with timeout
        timeout = 3600  # 1 hour timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                status = client._request_with_retry('GET', f'/scraping/status/{job_id}')
                status_data = status.json()
                
                if status_data['status'] in ['completed', 'failed', 'cancelled']:
                    return status_data
                
                time.sleep(10)  # Poll every 10 seconds
                
            except Exception as e:
                client.handle_api_error(e, f"while monitoring job {job_id}")
                time.sleep(30)  # Wait longer on error
        
        # Timeout reached
        client.logger.error(f"Job {job_id} monitoring timed out")
        return None
        
    except Exception as e:
        client.handle_api_error(e, "during job execution")
        return None
```

## Part 10: Complete Integration Example

### 10.1 Production-Ready Integration

**Complete E-commerce Monitoring System**:
```python
import schedule
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ProductMonitor:
    name: str
    template_id: str
    target_url: str
    check_frequency: str  # '1h', '6h', '1d'
    price_alert_threshold: Optional[float] = None
    stock_alert: bool = False

class EcommerceMonitoringSystem:
    def __init__(self, client: ScraperV4Client, db_integration: DatabaseIntegration):
        self.client = client
        self.db = db_integration
        self.monitors: List[ProductMonitor] = []
        self.alerts_config = {}
    
    def add_monitor(self, monitor: ProductMonitor):
        """Add a new product monitor"""
        self.monitors.append(monitor)
        
        # Schedule the monitor
        if monitor.check_frequency == '1h':
            schedule.every().hour.do(self.run_monitor, monitor)
        elif monitor.check_frequency == '6h':
            schedule.every(6).hours.do(self.run_monitor, monitor)
        elif monitor.check_frequency == '1d':
            schedule.every().day.do(self.run_monitor, monitor)
    
    def run_monitor(self, monitor: ProductMonitor):
        """Execute a single monitor"""
        print(f"Running monitor: {monitor.name}")
        
        job_config = {
            "name": f"Monitor: {monitor.name}",
            "template_id": monitor.template_id,
            "target_url": monitor.target_url,
            "options": {
                "stealth_mode": "medium",
                "max_pages": 1,  # Only monitor first page
                "quick_scan": True
            }
        }
        
        try:
            job_id = start_scraping_job(self.client, job_config)
            final_status = monitor_job_progress(self.client, job_id)
            
            if final_status['status'] == 'completed':
                results = get_job_results(self.client, job_id)
                self.process_monitor_results(monitor, results['data'])
            
        except Exception as e:
            print(f"Monitor {monitor.name} failed: {str(e)}")
    
    def process_monitor_results(self, monitor: ProductMonitor, data: List[Dict]):
        """Process monitor results and trigger alerts"""
        
        for item in data:
            # Check price alerts
            if monitor.price_alert_threshold and 'price' in item:
                try:
                    price = float(item['price'].replace('$', '').replace(',', ''))
                    if price <= monitor.price_alert_threshold:
                        self.send_price_alert(monitor, item, price)
                except ValueError:
                    pass  # Skip if price can't be parsed
            
            # Check stock alerts
            if monitor.stock_alert and 'availability' in item:
                if 'in stock' in item['availability'].lower():
                    self.send_stock_alert(monitor, item)
        
        # Save results to database
        timestamp = datetime.now().isoformat()
        self.db.save_monitor_results(monitor.name, data, timestamp)
    
    def send_price_alert(self, monitor: ProductMonitor, item: Dict, price: float):
        """Send price drop alert"""
        message = f"Price Alert: {item.get('title', 'Product')} is now ${price:.2f} (threshold: ${monitor.price_alert_threshold})"
        self.send_notification(message, 'price_alert')
    
    def send_stock_alert(self, monitor: ProductMonitor, item: Dict):
        """Send stock availability alert"""
        message = f"Stock Alert: {item.get('title', 'Product')} is back in stock!"
        self.send_notification(message, 'stock_alert')
    
    def send_notification(self, message: str, alert_type: str):
        """Send notification (email, Slack, etc.)"""
        print(f"[{alert_type.upper()}] {message}")
        # Implement your notification logic here
    
    def run_scheduler(self):
        """Run the monitoring scheduler"""
        print("Starting monitoring system...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

# Setup and usage
def setup_ecommerce_monitoring():
    """Setup complete ecommerce monitoring system"""
    
    client = RobustScraperV4Client()
    db_integration = DatabaseIntegration("ecommerce_monitoring.db")
    monitoring_system = EcommerceMonitoringSystem(client, db_integration)
    
    # Add monitors for different products
    monitors = [
        ProductMonitor(
            name="iPhone Price Monitor",
            template_id="apple_products_template",
            target_url="https://apple.com/iphone",
            check_frequency="6h",
            price_alert_threshold=900.0
        ),
        ProductMonitor(
            name="Gaming Laptop Monitor",
            template_id="laptop_template",
            target_url="https://example-tech.com/gaming-laptops",
            check_frequency="1d",
            price_alert_threshold=1500.0,
            stock_alert=True
        )
    ]
    
    for monitor in monitors:
        monitoring_system.add_monitor(monitor)
    
    # Start the monitoring system
    monitoring_system.run_scheduler()

# Run the monitoring system
if __name__ == "__main__":
    setup_ecommerce_monitoring()
```

## API Reference Summary

### Core Endpoints Quick Reference

**Templates**:
- `GET /api/templates` - List templates
- `POST /api/templates` - Create template
- `GET /api/templates/{id}` - Get template
- `PUT /api/templates/{id}` - Update template
- `DELETE /api/templates/{id}` - Delete template
- `POST /api/templates/{id}/test` - Test template

**Scraping**:
- `POST /api/scraping/start` - Start job
- `GET /api/scraping/status/{job_id}` - Get status
- `POST /api/scraping/pause/{job_id}` - Pause job
- `POST /api/scraping/resume/{job_id}` - Resume job
- `DELETE /api/scraping/cancel/{job_id}` - Cancel job

**Data**:
- `GET /api/data/results/{job_id}` - Get results
- `POST /api/data/export` - Export data
- `GET /api/data/jobs` - List jobs

**Monitoring**:
- `GET /api/monitoring/status` - System status
- `GET /api/monitoring/metrics` - Performance metrics

## Best Practices Summary

### API Integration Best Practices

1. **Error Handling**: Always implement comprehensive error handling
2. **Retry Logic**: Use exponential backoff for transient failures
3. **Rate Limiting**: Respect API rate limits and implement backoff
4. **Authentication**: Secure your API endpoints in production
5. **Monitoring**: Implement health checks and performance monitoring
6. **Logging**: Log all API interactions for debugging
7. **Testing**: Test your integrations thoroughly before production

### Performance Optimization

1. **Connection Pooling**: Reuse HTTP connections
2. **Async Operations**: Use async/await for I/O operations
3. **Batch Operations**: Batch multiple operations when possible
4. **Caching**: Cache frequently accessed data
5. **Streaming**: Use streaming for large datasets

## Summary

You've now mastered ScraperV4's complete API including:

1. **Authentication and Setup**: Secure API access and client configuration
2. **Template Management**: Programmatic template creation and testing
3. **Job Operations**: Automated job management and monitoring
4. **Data Integration**: Database integration and export automation
5. **Workflow Automation**: Complex pipeline creation and execution
6. **Error Handling**: Robust error handling and recovery strategies
7. **Monitoring**: Real-time monitoring and alerting systems

### Next Steps

- Implement the **Troubleshooting Guide** strategies for complex scenarios
- Build custom dashboards using the monitoring APIs
- Create specialized integrations for your specific use cases
- Explore advanced automation patterns for enterprise deployments

You're now equipped to build production-grade applications that leverage ScraperV4's full capabilities!