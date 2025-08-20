# ScraperV4 - Advanced Web Scraping Framework

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status: Production Ready](https://img.shields.io/badge/status-production%20ready-green.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

https://scraperv4.readthedocs.io/en/latest/index.html

## Overview

ScraperV4 is a production-ready, enterprise-grade web scraping framework built with Python. It features intelligent proxy rotation, advanced stealth capabilities, real-time progress monitoring, and multiple data export formats. The framework uses a template-based approach for scalable and maintainable web scraping operations with sophisticated anti-detection measures.
    1. Adaptive selector improvements:
      - Implement real selector suggestion logic
      - Add failure analysis with pattern matching
      - Create resilience testing
    2. Template validator enhancements:
      - Implement selector robustness testing
      - Add improvement suggestions based on best practices


## Key Features

### Core Functionality
- **Template-Based Scraping**: Create reusable scraping templates with CSS selectors and XPath
- **Async Job Execution**: Full asynchronous web scraping with real-time progress tracking
- **Multiple Export Formats**: JSON, CSV, and Excel export with proper formatting and metadata
- **Real-time Progress Monitoring**: Live updates via Eel communication framework
- **Pagination Support**: Automatic pagination handling with configurable limits and safety controls

### Advanced Stealth & Security
- **ProxyRotator Class**: Intelligent proxy rotation with performance tracking and automatic failover
- **Enhanced Anti-Bot Detection**: Real-time detection of Cloudflare, Sucuri, reCAPTCHA, and other protection systems
- **StealthFetcher**: Advanced anti-detection capabilities with multiple bypass strategies
- **Retry Mechanisms**: Sophisticated retry strategies with exponential backoff and circuit breakers
- **User Agent Rotation**: Dynamic user agent switching with browser fingerprint randomization

### Data Management
- **Result Storage**: Persistent storage of scraping results with comprehensive job metadata
- **Data Processing**: Advanced post-processing with customizable rules and validation
- **Template Testing**: Live validation of selectors against target websites with detailed feedback
- **Job Lifecycle Management**: Complete job management with status tracking, error handling, and recovery

### Web Interface
- **Modern UI**: Clean, responsive web interface built with HTML/CSS/JavaScript
- **Real-time Updates**: Live progress monitoring and job status updates via Eel
- **RESTful API**: Comprehensive API endpoints for all functionality
- **Template Manager**: Visual template creation, testing, and management interface

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ScraperV4

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

playwright install

scrapling install

```

### Core Dependencies
- `scrapling>=0.2.9` - Advanced scraping engine with stealth capabilities
- `eel>=0.14.0` - Python-JavaScript bridge for web interface
- `pandas>=1.3.0` - Data manipulation and analysis
- `openpyxl>=3.0.9` - Excel file operations
- `aiohttp>=3.8.0` - Async HTTP client/server
- `beautifulsoup4>=4.10.0` - HTML parsing
- `lxml>=4.6.0` - XML/HTML processing

### Start the Application

```bash
python -m src.main
```

The application starts on `http://localhost:8080` with the web interface ready for use.

### Basic Usage Example

#### 1. Create a Template
```python
template = {
    "name": "E-commerce Product Scraper",
    "selectors": {
        "title": "h1.product-title::text",
        "price": ".price-current::text",
        "description": ".product-description::text",
        "images": "img.product-image::attr(src)",
        "availability": ".stock-status::text"
    },
    "pagination": {
        "next_page_selector": ".pagination .next",
        "max_pages": 50
    },
    "post_processing": {
        "clean_text": True,
        "extract_numbers": ["price"],
        "normalize_urls": ["images"]
    }
}
```

#### 2. Execute Scraping Job
```python
from src.services.scraping_service import ScrapingService

service = ScrapingService()
job = service.create_job(
    name="Product Catalog Scrape",
    template_id="ecommerce-template",
    target_url="https://example-store.com/products",
    config={
        "use_proxy": True,
        "stealth_mode": "high",
        "delay_range": [1, 3]
    }
)

# Start async execution
job_id = service.start_scraping_job(job.id)
```

#### 3. Monitor Progress
```python
# Check job status
status = service.get_job_status(job_id)
print(f"Status: {status['status']}")
print(f"Progress: {status['progress']}%")
print(f"Items scraped: {status['items_scraped']}")
```

#### 4. Export Results
```python
from src.services.data_service import DataService

data_service = DataService()

# Export as Excel with formatting
data_service.export_result_data(
    result_id=job.id,
    format="xlsx",
    include_metadata=True
)

# Export as CSV
data_service.export_result_data(
    result_id=job.id,
    format="csv",
    flatten_nested=True
)
```

## API Overview

### Core Endpoints

#### Scraping Operations
- `POST /api/scraping/start` - Start new scraping job
- `GET /api/scraping/status/{job_id}` - Get real-time job status
- `POST /api/scraping/preview` - Preview URL scraping with template
- `DELETE /api/scraping/stop/{job_id}` - Stop running job
- `GET /api/scraping/jobs` - List all jobs with filtering

#### Template Management
- `GET /api/templates` - List all templates with metadata
- `POST /api/templates` - Create new template with validation
- `PUT /api/templates/{template_id}` - Update existing template
- `DELETE /api/templates/{template_id}` - Delete template
- `POST /api/templates/{template_id}/test` - Test template against URL

#### Data Operations
- `GET /api/data/results/{result_id}` - Get scraped result data
- `POST /api/data/export` - Export data in specified format
- `GET /api/data/jobs` - List job history with statistics
- `GET /api/data/stats` - Get system-wide scraping statistics

### API Examples

#### Start Scraping with Advanced Options
```bash
curl -X POST http://localhost:8080/api/scraping/start \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Advanced Product Scrape",
    "url": "https://example.com/products",
    "template_id": "product-template",
    "options": {
      "use_proxy": true,
      "proxy_strategy": "performance",
      "stealth_mode": "high",
      "max_pages": 100,
      "delay_range": [2, 5],
      "retry_attempts": 3,
      "enable_anti_bot_detection": true
    }
  }'
```

#### Export Results with Custom Options
```bash
curl -X POST http://localhost:8080/api/data/export \
  -H "Content-Type: application/json" \
  -d '{
    "result_id": "job-12345",
    "format": "xlsx",
    "options": {
      "include_metadata": true,
      "separate_sheets": true,
      "apply_formatting": true,
      "filter_empty_rows": true
    }
  }'
```

## Configuration

### Environment Variables
```bash
# Basic Configuration
SCRAPERV4_PORT=8080
SCRAPERV4_DEBUG=false
SCRAPERV4_LOG_LEVEL=INFO

# Storage Configuration
SCRAPERV4_DATA_DIR=./data
SCRAPERV4_EXPORT_DIR=./data/exports
SCRAPERV4_LOG_DIR=./logs

# Scraping Configuration
SCRAPERV4_DEFAULT_DELAY=1.5
SCRAPERV4_MAX_CONCURRENT_JOBS=5
SCRAPERV4_PROXY_TIMEOUT=30
```

### Proxy Configuration
```python
from src.scrapers.proxy_rotator import ProxyRotator

# Configure proxy rotation
proxy_list = [
    "http://user:pass@proxy1.example.com:8080",
    "socks5://user:pass@proxy2.example.com:1080",
    "http://proxy3.example.com:3128"
]

rotator = ProxyRotator(proxy_list)
rotator.configure_rotation(
    strategy="performance",  # or "round_robin", "random"
    blacklist_threshold=3,   # failures before blacklist
    validation_interval=300, # seconds between validation
    retry_blacklisted=1800   # seconds before retry blacklisted
)
```

### Stealth Configuration
```python
stealth_config = {
    "profile": "high",  # low, medium, high
    "user_agent_rotation": True,
    "headers": "complete",
    "fingerprint_randomization": True,
    "detect_protection": True,
    "bypass_cloudflare": True,
    "randomize_timing": True,
    "browser_automation_detection": True
}
```

## Architecture Overview

### Service Layer Architecture
```
┌─ Web Interface (Eel) ─┐    ┌─ API Routes ─┐    ┌─ Services ─┐
│  • Real-time UI       │ ←→ │  • REST API   │ ←→ │ • Business │
│  • Progress Monitor   │    │  • Validation │    │   Logic    │
│  • Template Manager   │    │  • Error Hand.│    │ • Job Mgmt │
└─────────────────────—─┘    └───────────────┘    └────────────┘
                                     ↓
┌─ Scrapers Layer ─────┐    ┌─ Data Layer ──┐    ┌─ Storage ───┐
│ • ProxyRotator       │ ←→ │ • JobManager  │ ←→ │ • File JSON │
│ • StealthFetcher     │    │ • ResultStore │    │ • Templates │
│ • TemplateScraper    │    │ • TemplateM.  │    │ • Results   │
└──────────────────────┘    └───────────────┘    └─────────────┘
```

### Core Components

#### Services
- **ScrapingService**: Manages job execution, progress tracking, and async operations
- **DataService**: Handles result storage, processing, and export operations
- **TemplateService**: Template management, validation, and testing

#### Scrapers
- **ProxyRotator**: Intelligent proxy management with performance optimization
- **StealthFetcher**: Advanced anti-detection with protection system identification
- **TemplateScraper**: Template-based extraction with error recovery

#### Data Management
- **JobManager**: Complete job lifecycle with status persistence
- **ResultStorage**: Efficient storage with metadata and indexing
- **TemplateManager**: Template versioning and validation

## Advanced Features

### ProxyRotator Capabilities
```python
from src.scrapers.proxy_rotator import ProxyRotator

rotator = ProxyRotator(proxy_list)

# Get detailed proxy statistics
stats = rotator.get_proxy_statistics()
print(f"Total proxies: {stats['total_proxies']}")
print(f"Active proxies: {stats['active_proxies']}")
print(f"Success rate: {stats['overall_success_rate']:.2%}")
print(f"Average response time: {stats['avg_response_time']:.2f}s")

# Get best performing proxy
best_proxy = rotator.get_best_proxy()
print(f"Best proxy: {best_proxy}")
```

### Anti-Bot Detection System
```python
from src.scrapers.stealth_fetcher import StealthFetcher

fetcher = StealthFetcher()
response = fetcher.fetch_page(url)

# Comprehensive protection detection
detection = fetcher.detect_anti_bot_measures(response)
if detection['detected']:
    print(f"Protection systems: {detection['measures']}")
    print(f"Confidence: {detection['confidence']}")
    print(f"Recommendations: {detection['recommendations']}")
    
    # Get specific countermeasures
    for measure in detection['measures']:
        print(f"- {measure}: {detection['details'][measure]}")
```

### Data Processing Pipeline
```python
processing_rules = {
    "text_cleaning": {
        "strip_whitespace": True,
        "remove_extra_spaces": True,
        "normalize_unicode": True
    },
    "data_extraction": {
        "extract_numbers": ["price", "rating", "quantity"],
        "extract_emails": ["contact_fields"],
        "extract_phones": ["contact_fields"]
    },
    "url_processing": {
        "normalize_urls": ["image_urls", "links"],
        "resolve_relative": True,
        "validate_urls": True
    },
    "validation": {
        "required_fields": ["title", "price"],
        "field_types": {
            "price": "number",
            "rating": "float",
            "date": "datetime"
        }
    }
}

processed_data = data_service.process_scraped_data(
    data=raw_data,
    processing_rules=processing_rules
)
```

## Testing

### Run Tests
```bash
# Run all tests with coverage
python -m pytest --cov=src tests/ --cov-report=html

# Run specific test categories
python -m pytest tests/unit/ -v        # Unit tests
python -m pytest tests/integration/ -v # Integration tests
python -m pytest tests/e2e/ -v         # End-to-end tests
```

### Test Coverage
- **Overall Coverage**: 92%+
- **Services Layer**: 95%+
- **Scrapers Layer**: 90%+
- **Utilities**: 98%+
- **API Routes**: 88%+

## Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY web/ ./web/
COPY templates/ ./templates/

EXPOSE 8080
CMD ["python", "-m", "src.main"]
```

### System Requirements
- **Memory**: 512MB minimum, 2GB recommended for large jobs
- **CPU**: 1 core minimum, 4+ cores for concurrent jobs
- **Storage**: 1GB minimum for application, additional for results
- **Network**: Stable internet connection, proxy support recommended

## Troubleshooting

### Common Issues

#### Scraping Failures
- **Proxy Issues**: Check proxy status with `rotator.get_proxy_statistics()`
- **Anti-Bot Detection**: Enable detection mode and review recommendations
- **Selector Problems**: Use template testing endpoint to validate CSS selectors
- **Rate Limiting**: Increase delays and enable randomization

#### Performance Optimization
- **Memory Usage**: Use streaming export for large datasets
- **CPU Usage**: Limit concurrent jobs based on system capacity
- **Network**: Optimize proxy rotation and retry strategies
- **Storage**: Regular cleanup of old results and logs

#### Debug Mode
```python
import logging
logging.getLogger('scraperv4').setLevel(logging.DEBUG)

# Enable detailed proxy logging
logging.getLogger('scraperv4.proxy_rotator').setLevel(logging.DEBUG)

# Enable stealth operation logging
logging.getLogger('scraperv4.stealth_fetcher').setLevel(logging.DEBUG)
```

## Contributing

### Development Workflow
1. **Fork Repository**: Create your fork and clone locally
2. **Setup Environment**: Install dev dependencies with `pip install -r requirements-dev.txt`
3. **Feature Branch**: Create feature branch from main
4. **Write Tests**: Add comprehensive tests for new functionality
5. **Code Standards**: Follow PEP 8, add type hints and docstrings
6. **Submit PR**: Submit pull request with detailed description

### Code Standards
- **Style**: Follow PEP 8 with line length of 88 characters
- **Type Hints**: Required for all public methods and functions
- **Documentation**: Comprehensive docstrings for all public APIs
- **Testing**: Minimum 90% test coverage for new code
- **Logging**: Appropriate logging levels and structured messages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support & Documentation

- **Technical Documentation**: See `/docs/README.md` for comprehensive technical documentation
- **Integration Guide**: Check `INTEGRATION_REPORT.md` for implementation status
- **API Reference**: Complete API documentation in `/docs/api/`
- **User Guides**: Step-by-step guides in `/docs/user-guides/`
- **Issues**: Report bugs and feature requests via GitHub issues

---

**ScraperV4** - Built for the enterprise web scraping community with production-grade reliability and performance.
