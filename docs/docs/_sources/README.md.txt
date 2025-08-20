# ScraperV4 Technical Documentation

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Interactive Visual Template Creation](#interactive-visual-template-creation)
3. [Core Components](#core-components)
4. [API Reference](#api-reference)
5. [Frontend Integration](#frontend-integration)
6. [Advanced Features](#advanced-features)
7. [Testing & Development](#testing--development)
8. [Troubleshooting](#troubleshooting)

## Architecture Overview

### System Architecture

ScraperV4 follows a modular, service-oriented architecture with clear separation of concerns:

```
┌─────────────────── Application Layer ──────────────────┐
│                                                         │
│  ┌─ Web Interface (Eel)  ─┐    ┌─ API Routes Layer ─┐   │
│  │ • Real-time UI         │ ←→ │ • REST Endpoints   │   │
│  │ • Progress Monitor     │    │ • Input Validation │   │
│  │ • Template Manager     │    │ • Error Handling   │   │
│  │ • Results Viewer       │    │ • Response Format  │   │
│  │ • Interactive Selector │    │ • Visual Creation  │   │
│  └────────────────────────┘    └────────────────────┘   │
│                          ↓                              │
└─────────────────────────────────────────────────────────┘
┌─────────────────── Business Logic Layer ────────────────┐
│                                                         │
│  ┌─ Services Layer ─────┐    ┌─ Dependency Injection ─┐ │
│  │ • ScrapingService    │ ←→ │ • Service Container    │ │
│  │ • DataService        │    │ • Configuration        │ │
│  │ • TemplateService    │    │ • Lifecycle Mgmt       │ │
│  │ • InteractiveService │    │ • Pattern Recognition  │ │
│  └──────────────────────┘    └────────────────────────┘ │
│                          ↓                              │
└─────────────────────────────────────────────────────────┘
┌─────────────────── Processing Layer ────────────────────┐
│                                                         │
│  ┌─ Scrapers ─────────┐    ┌─ Templates ────────────┐   │
│  │ • ProxyRotator     │    │ • TemplateManager      │   │
│  │ • StealthFetcher   │ ←→ │ • AdaptiveSelector     │   │
│  │ • TemplateScraper  │    │ • TemplateValidator    │   │
│  │ • BaseScraper      │    └────────────────────────┘   │
│  └────────────────────┘                                 │
│                          ↓                              │
└─────────────────────────────────────────────────────────┘
┌─────────────────── Data & Storage Layer ─────────────────┐
│                                                          │
│  ┌─ Data Management ──┐    ┌─ Storage ──────────────┐    │
│  │ • JobManager       │ ←→ │ • JSON File Storage    │    │
│  │ • ResultStorage    │    │ • Template Storage     │    │
│  │ • TemplateManager  │    │ • Export Files         │    │
│  └────────────────────┘    │ • Logs & Metadata      │    │
│                            └────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

### Directory Structure

```
src/
├── main.py                    # Application entry point
├── core/                      # Core system components
│   ├── config.py             # Configuration management
│   └── container.py          # Dependency injection container
├── web/                       # Web interface & API layer
│   ├── eel_app.py            # Eel application wrapper
│   └── api_routes.py         # API route definitions & handlers
├── services/                  # Business logic services
│   ├── base_service.py       # Base service class
│   ├── scraping_service.py   # Scraping operations & job management
│   ├── template_service.py   # Template CRUD & validation
│   ├── data_service.py       # Data processing & export
│   └── interactive_service.py # Interactive visual template creation
├── scrapers/                  # Scraping implementation layer
│   ├── base_scraper.py       # Base scraper interface
│   ├── stealth_fetcher.py    # Anti-detection fetching
│   ├── template_scraper.py   # Template-based extraction
│   ├── fetcher_manager.py    # Fetcher coordination
│   └── proxy_rotator.py      # Proxy management & rotation
├── templates/                 # Template system
│   ├── template_manager.py   # Template storage & retrieval
│   ├── adaptive_selector.py  # Self-healing selectors
│   └── template_validator.py # Template validation logic
├── data/                      # Data management layer
│   ├── job_manager.py        # Job lifecycle management
│   ├── result_storage.py     # Result persistence & retrieval
│   └── template_manager.py   # Template data operations
└── utils/                     # Utility functions
    ├── logging_utils.py      # Logging configuration
    ├── data_utils.py         # Data export utilities
    └── validation_utils.py   # Input validation helpers
```

## Interactive Visual Template Creation

ScraperV4 features a powerful interactive visual template creation system that allows users to create scraping templates through point-and-click interactions without writing code.

### Key Features

- **Visual Element Selection**: Click on elements to add them to your template
- **AI-Powered Auto-Detection**: Automatically identifies patterns and suggests fields
- **Container Recognition**: Detects repeating elements for list/grid extraction
- **Real-time Validation**: Test selectors as you build your template
- **Learning System**: Improves pattern recognition from user corrections
- **Cross-Site Reusability**: Templates adapt to similar website structures

### Quick Start

1. **Access Interactive Mode**
   ```javascript
   // Click the Interactive Mode button in Template Manager
   // Or programmatically:
   await eel.start_interactive_mode('https://target-site.com')();
   ```

2. **Select Elements Visually**
   - Hover over elements to highlight them
   - Click to select and add to template
   - Use container mode for repeating elements

3. **Auto-Detection**
   ```javascript
   // System automatically detects:
   - Site type (e-commerce, news, directory)
   - Product containers and fields
   - Pagination elements
   - Common patterns (prices, titles, images)
   ```

4. **Save and Export**
   - Templates are automatically generated from selections
   - Export for reuse across similar sites
   - Includes fallback selectors for robustness

### Architecture Components

#### Frontend (JavaScript)
- **InteractiveOverlay**: Visual selection interface
- **AutoDetector**: Pattern recognition engine
- **SelectorGenerator**: Creates robust CSS/XPath selectors
- **SimilarityScorer**: Finds matching elements

#### Backend (Python)
- **InteractiveService**: Orchestrates template generation
- **PatternRecognizer**: Classifies sites and detects patterns
- **LearningSystem**: Improves detection through corrections
- **TemplateGenerator**: Creates templates from selections

### Interactive API

```python
# Python API
from src.services.interactive_service import InteractiveService

service = InteractiveService()
analysis = service.analyze_page_structure(url)
template = service.generate_template_from_selection(selections)
```

```javascript
// JavaScript API
const overlay = new InteractiveOverlay({
    targetDocument: document,
    callbacks: {
        onElementSelected: handleSelection,
        onContainerFound: handleContainer
    }
});

// Auto-detect patterns
const detector = new AutoDetector();
const siteType = detector.detectSiteType(document);
const containers = detector.detectContainers(document);
```

### Documentation

- **[Interactive Selection Tutorial](/docs/tutorials/interactive-selection.md)**: Step-by-step guide to using the interactive selector
- **[Visual Template Creation Guide](/docs/how-to/visual-template-creation.md)**: Practical recipes for common scenarios
- **[Interactive Architecture](/docs/explanations/interactive-architecture.md)**: Deep dive into system architecture and design
- **[Interactive API Reference](/docs/reference/interactive-api.md)**: Complete API documentation

### Benefits

1. **Accessibility**: No coding required - anyone can create templates
2. **Speed**: Visual selection is faster than writing selectors
3. **Accuracy**: AI assistance reduces errors
4. **Adaptability**: Templates self-heal when sites change
5. **Learning**: System improves over time

## Core Components

### Service Layer

#### ScrapingService (`src/services/scraping_service.py`)

**Primary Functions:**
- Job creation and management
- Asynchronous scraping execution
- Progress monitoring and broadcasting
- Error handling and recovery

**Key Methods:**
```python
class ScrapingService:
    def create_job(name: str, template_id: str, target_url: str, 
                   config: Dict = None, parameters: Dict = None) -> JobData
    
    async def execute_job_async(job_id: str) -> None
    
    def start_scraping_job(job_id: str) -> str
    
    def get_job_status(job_id: str) -> Dict[str, Any]
    
    def stop_job(job_id: str) -> bool
    
    def list_jobs(status_filter: str = None, limit: int = 50) -> List[Dict]
```

**Real-time Progress Broadcasting:**
```python
def _broadcast_job_progress(self, job_data: Dict[str, Any]) -> None:
    """Broadcast job progress updates via Eel to connected clients."""
    try:
        import eel
        # Send progress update to all connected clients
        eel.updateJobProgress(job_data)
    except Exception as e:
        # Non-blocking error handling for broadcast failures
        self.logger.warning(f"Failed to broadcast progress: {e}")
```

#### DataService (`src/services/data_service.py`)

**Primary Functions:**
- Result data processing and storage
- Multi-format export (JSON, CSV, Excel)
- Data validation and cleaning
- Storage statistics and management

**Export Functionality:**
```python
def export_result_data(self, result_id: str, format: str = "json", 
                      include_metadata: bool = True, **options) -> str:
    """Export result data to specified format."""
    
    # Format-specific implementations:
    # - JSON: Pretty-printed with metadata
    # - CSV: Flattened nested structures
    # - Excel: Formatted sheets with styling
```

**Data Processing Pipeline:**
```python
def process_scraped_data(self, data: Any, processing_rules: Dict = None) -> Any:
    """Process scraped data using TemplateScraper post-processing."""
    # Uses actual template scraper logic for consistency
    # Handles both single items and lists
    # Applies cleaning, validation, and transformation rules
```

#### TemplateService (`src/services/template_service.py`)

**Primary Functions:**
- Template CRUD operations
- Live template testing and validation
- Template statistics and metrics
- Selector optimization

**Template Testing (Real Implementation):**
```python
async def test_template(self, template_id: str, test_url: str) -> Dict[str, Any]:
    """Test template against URL with actual scraping."""
    
    # Uses TemplateScraper for real validation
    # Returns actual extracted data samples
    # Updates template statistics based on results
    # Provides detailed validation feedback
```

#### InteractiveService (`src/services/interactive_service.py`)

**Primary Functions:**
- Visual template creation through point-and-click
- AI-powered pattern recognition
- Learning from user corrections
- Template generation from selections

**Key Methods:**
```python
class InteractiveService:
    def analyze_page_structure(url: str) -> Dict[str, Any]:
        """Analyze page for interactive selection."""
        
    def suggest_selectors(html: str, element_info: Dict) -> List[str]:
        """Generate selector suggestions."""
        
    def validate_selector(selector: str, html: str) -> Dict[str, Any]:
        """Validate selector against HTML."""
        
    def generate_template_from_selection(selections: Dict) -> Dict[str, Any]:
        """Create template from visual selections."""
        
    def apply_learning_corrections(corrections: Dict) -> bool:
        """Learn from user corrections."""
```

**Pattern Recognition:**
```python
def detect_patterns(self, soup: BeautifulSoup) -> Dict[str, Any]:
    """Detect common patterns in web pages."""
    # Identifies:
    # - E-commerce product listings
    # - News articles
    # - Directory listings
    # - Real estate properties
    # Returns confidence scores and suggestions
```

### Scraper Layer

#### ProxyRotator (`src/scrapers/proxy_rotator.py`)

**Intelligent Proxy Management:**
```python
class ProxyRotator:
    def __init__(self, proxy_list: List[str] = None):
        # Performance tracking per proxy
        self.proxy_stats = {
            proxy: {
                'successes': 0,
                'failures': 0,
                'response_times': [],
                'blacklisted_until': None,
                'last_used': None
            }
            for proxy in proxy_list
        }
    
    def get_next_proxy(self) -> Optional[str]:
        """Get next working proxy based on performance."""
        
    def configure_rotation(self, strategy: str = "performance",
                          blacklist_threshold: int = 3,
                          validation_interval: int = 300):
        """Configure rotation strategy and parameters."""
    
    def get_proxy_statistics(self) -> Dict[str, Any]:
        """Get comprehensive proxy performance statistics."""
```

**Features:**
- **Performance-based selection**: Chooses best-performing proxies
- **Automatic blacklisting**: Removes failing proxies with exponential backoff
- **Health monitoring**: Tracks response times and success rates
- **Multiple strategies**: Round-robin, random, or performance-based rotation

#### StealthFetcher (`src/scrapers/stealth_fetcher.py`)

**Enhanced Anti-Bot Detection:**
```python
def detect_anti_bot_measures(self, response) -> Dict[str, Any]:
    """Comprehensive anti-bot protection detection."""
    
    detection_results = {
        'detected': False,
        'measures': [],
        'confidence': 0.0,
        'recommendations': [],
        'details': {}
    }
    
    # Detection algorithms for:
    # - Cloudflare protection
    # - Sucuri WAF
    # - Rate limiting responses
    # - CAPTCHA systems (reCAPTCHA, hCaptcha)
    # - Browser fingerprinting
    # - JavaScript challenges
```

**Stealth Capabilities:**
- **Header randomization**: Complete browser-like headers
- **User agent rotation**: Realistic user agent switching
- **Timing randomization**: Human-like request patterns
- **Fingerprint management**: TLS and browser fingerprint handling

#### TemplateScraper (`src/scrapers/template_scraper.py`)

**Template-based Extraction:**
- Supports CSS selectors and XPath expressions
- Handles pagination with safety limits
- Provides post-processing pipeline
- Includes error recovery and fallback selectors

### Data Management Layer

#### JobManager (`src/data/job_manager.py`)

**Job Lifecycle Management:**
```python
class JobManager:
    def create_job(self, name: str, template_name: str, target_url: str,
                   job_config: Dict = None, parameters: Dict = None) -> Dict
    
    def update_job_status(self, job_id: str, status: str, 
                         progress: int = None, **updates) -> bool
    
    def get_job(self, job_id: str) -> Optional[Dict]
    
    def list_jobs(self, status_filter: str = None, limit: int = 50) -> List[Dict]
```

**Features:**
- Persistent job storage with metadata
- Status tracking (pending, running, completed, failed)
- Progress monitoring with granular updates
- Error logging and recovery information

#### ResultStorage (`src/data/result_storage.py`)

**Result Persistence:**
- Efficient JSON-based storage
- Metadata tracking and indexing
- Result retrieval with filtering
- Storage optimization and cleanup

## API Reference

### Scraping Operations

#### Start Scraping Job
```http
POST /api/scraping/start
Content-Type: application/json

{
  "name": "Job Name",
  "url": "https://target-site.com",
  "template_id": "template-123",
  "options": {
    "use_proxy": true,
    "stealth_mode": "high",
    "max_pages": 100,
    "delay_range": [1, 3],
    "retry_attempts": 3
  }
}
```

**Response:**
```json
{
  "job_id": "uuid-job-id",
  "status": "pending",
  "created_at": "2025-08-16T10:30:00Z",
  "estimated_duration": 300
}
```

#### Get Job Status
```http
GET /api/scraping/status/{job_id}
```

**Response:**
```json
{
  "job_id": "uuid-job-id",
  "status": "running",
  "progress": 65,
  "items_scraped": 1250,
  "items_failed": 15,
  "current_page": 13,
  "estimated_completion": "2025-08-16T10:45:00Z",
  "errors": [
    {
      "timestamp": "2025-08-16T10:35:00Z",
      "error": "Proxy timeout",
      "url": "https://target-site.com/page/8"
    }
  ]
}
```

#### Preview URL Scraping
```http
POST /api/scraping/preview
Content-Type: application/json

{
  "url": "https://example.com",
  "template_id": "template-123",
  "options": {
    "limit_results": 5
  }
}
```

**Response:**
```json
{
  "success": true,
  "preview_data": [
    {
      "title": "Product Name",
      "price": "$29.99",
      "description": "Product description..."
    }
  ],
  "validation": {
    "selectors_working": 4,
    "selectors_total": 5,
    "success_rate": 0.8
  }
}
```

### Template Management

#### Create Template
```http
POST /api/templates
Content-Type: application/json

{
  "name": "E-commerce Template",
  "selectors": {
    "title": "h1.product-title::text",
    "price": ".price::text",
    "description": ".description::text"
  },
  "pagination": {
    "next_page_selector": ".next-page",
    "max_pages": 50
  },
  "post_processing": {
    "clean_text": true,
    "extract_numbers": ["price"]
  }
}
```

#### Test Template
```http
POST /api/templates/{template_id}/test
Content-Type: application/json

{
  "test_url": "https://target-site.com/product/123"
}
```

**Response:**
```json
{
  "success": true,
  "sample_data": {
    "title": "Sample Product",
    "price": "29.99",
    "description": "Sample description"
  },
  "validation_results": {
    "working_selectors": ["title", "price", "description"],
    "failed_selectors": [],
    "success_rate": 1.0,
    "extraction_time": 0.85
  }
}
```

### Data Operations

#### Export Results
```http
POST /api/data/export
Content-Type: application/json

{
  "result_id": "job-uuid",
  "format": "xlsx",
  "options": {
    "include_metadata": true,
    "separate_sheets": true,
    "apply_formatting": true
  }
}
```

**Response:**
```json
{
  "export_path": "/exports/job-uuid_20250816_103000.xlsx",
  "format": "xlsx",
  "file_size": 2048576,
  "record_count": 1500,
  "export_time": "2025-08-16T10:30:00Z"
}
```

#### Get System Statistics
```http
GET /api/data/stats
```

**Response:**
```json
{
  "total_jobs": 145,
  "completed_jobs": 132,
  "failed_jobs": 8,
  "pending_jobs": 5,
  "total_items_scraped": 45230,
  "storage_usage": {
    "total_size_mb": 256.7,
    "results_size_mb": 198.3,
    "exports_size_mb": 58.4
  },
  "average_job_duration": 425,
  "success_rate": 0.945
}
```

## Frontend Integration

### Eel Communication Patterns

#### Real-time Progress Updates
```javascript
// Frontend: Listen for progress updates
eel.expose(updateJobProgress);
function updateJobProgress(progressData) {
    // Update progress bar
    document.getElementById('progress-bar').style.width = 
        progressData.progress + '%';
    
    // Update statistics
    document.getElementById('items-scraped').textContent = 
        progressData.items_scraped;
    
    // Update status
    document.getElementById('job-status').textContent = 
        progressData.status;
}

// Backend: Broadcast progress (from ScrapingService)
def _broadcast_job_progress(self, job_data):
    try:
        eel.updateJobProgress(job_data)
    except Exception as e:
        self.logger.warning(f"Failed to broadcast progress: {e}")
```

#### API Call Patterns
```javascript
// Call Python API from JavaScript
async function startScrapingJob(jobConfig) {
    try {
        const result = await eel.start_scraping_job(jobConfig)();
        return result;
    } catch (error) {
        console.error('Failed to start job:', error);
        throw error;
    }
}

// Export results
async function exportResults(resultId, format, options) {
    const exportPath = await eel.export_result_data(
        resultId, format, options
    )();
    return exportPath;
}
```

### Component Architecture

#### Progress Monitor Component
```javascript
class ProgressMonitor {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.activeJobs = new Map();
    }
    
    addJob(jobId, jobData) {
        // Create progress element
        // Setup real-time updates
        // Handle completion/failure
    }
    
    updateProgress(jobId, progressData) {
        // Update UI elements
        // Handle status changes
        // Trigger notifications
    }
}
```

#### Template Manager Component
```javascript
class TemplateManager {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.templates = [];
    }
    
    async loadTemplates() {
        this.templates = await eel.list_templates()();
        this.renderTemplateList();
    }
    
    async testTemplate(templateId, testUrl) {
        const results = await eel.test_template(templateId, testUrl)();
        this.displayTestResults(results);
    }
}
```

### Frontend File Structure
```
web/
├── index.html                 # Main application page
├── static/
│   ├── css/
│   │   ├── main.css          # Global styles
│   │   └── components/       # Component-specific styles
│   │       ├── progress-monitor.css
│   │       ├── scraping-form.css
│   │       └── results-table.css
│   ├── js/
│   │   ├── app.js           # Main application logic
│   │   ├── api.js           # API communication layer
│   │   ├── components/      # UI components
│   │   │   ├── progress-monitor.js
│   │   │   ├── template-manager.js
│   │   │   ├── scraping-form.js
│   │   │   └── results-table.js
│   │   └── utils/          # Utility functions
│   │       ├── helpers.js
│   │       ├── logger.js
│   │       └── notifications.js
│   └── images/             # Static images and icons
```

## Advanced Features

### Proxy Rotation System

#### Configuration Options
```python
from src.scrapers.proxy_rotator import ProxyRotator

# Initialize with proxy list
proxy_list = [
    "http://user:pass@proxy1.com:8080",
    "socks5://user:pass@proxy2.com:1080",
    "http://proxy3.com:3128"
]

rotator = ProxyRotator(proxy_list)

# Configure rotation strategy
rotator.configure_rotation(
    strategy="performance",        # performance, round_robin, random
    blacklist_threshold=3,         # failures before blacklisting
    validation_interval=300,       # seconds between health checks
    retry_blacklisted=1800,        # seconds before retry
    response_timeout=30,           # proxy timeout in seconds
    health_check_url="http://httpbin.org/ip"
)
```

#### Performance Monitoring
```python
# Get detailed statistics
stats = rotator.get_proxy_statistics()

{
    "total_proxies": 10,
    "active_proxies": 8,
    "blacklisted_proxies": 2,
    "overall_success_rate": 0.892,
    "avg_response_time": 1.34,
    "best_proxy": {
        "url": "http://proxy1.com:8080",
        "success_rate": 0.967,
        "avg_response_time": 0.89
    },
    "proxy_details": [
        {
            "proxy": "http://proxy1.com:8080",
            "successes": 145,
            "failures": 5,
            "success_rate": 0.967,
            "avg_response_time": 0.89,
            "last_used": "2025-08-16T10:29:45Z",
            "status": "active"
        }
    ]
}
```

### Anti-Bot Detection System

#### Detection Capabilities
```python
from src.scrapers.stealth_fetcher import StealthFetcher

fetcher = StealthFetcher()
response = fetcher.fetch_page(url)

detection = fetcher.detect_anti_bot_measures(response)

{
    "detected": True,
    "confidence": 0.95,
    "measures": ["cloudflare", "rate_limiting"],
    "recommendations": [
        "Increase request delays",
        "Use residential proxies",
        "Enable JavaScript rendering"
    ],
    "details": {
        "cloudflare": {
            "evidence": ["cf-ray header", "security challenge"],
            "protection_level": "medium"
        },
        "rate_limiting": {
            "evidence": ["429 status code", "retry-after header"],
            "limit_type": "ip_based"
        }
    }
}
```

#### Stealth Configuration Profiles
```python
# Low stealth profile
stealth_config = {
    "profile": "low",
    "user_agent_rotation": False,
    "header_randomization": "basic",
    "request_timing": "fast"
}

# Medium stealth profile
stealth_config = {
    "profile": "medium",
    "user_agent_rotation": True,
    "header_randomization": "complete",
    "request_timing": "varied",
    "fingerprint_randomization": True
}

# High stealth profile
stealth_config = {
    "profile": "high",
    "user_agent_rotation": True,
    "header_randomization": "complete",
    "request_timing": "human_like",
    "fingerprint_randomization": True,
    "tls_randomization": True,
    "javascript_execution": True,
    "captcha_detection": True
}
```

### Data Processing Pipeline

#### Processing Rules Configuration
```python
processing_rules = {
    "text_cleaning": {
        "strip_whitespace": True,
        "remove_extra_spaces": True,
        "normalize_unicode": True,
        "remove_html_tags": True,
        "decode_entities": True
    },
    "data_extraction": {
        "extract_numbers": ["price", "rating", "quantity", "year"],
        "extract_emails": ["contact", "support"],
        "extract_phones": ["contact", "support"],
        "extract_urls": ["links", "references"]
    },
    "data_transformation": {
        "normalize_urls": ["image_urls", "product_links"],
        "resolve_relative_urls": True,
        "currency_normalization": ["price", "cost"],
        "date_parsing": ["published_date", "modified_date"]
    },
    "validation": {
        "required_fields": ["title", "url"],
        "field_types": {
            "price": "number",
            "rating": "float",
            "quantity": "integer",
            "published_date": "datetime"
        },
        "value_ranges": {
            "rating": [0, 5],
            "price": [0, None]
        }
    },
    "post_processing": {
        "remove_duplicates": True,
        "sort_by": "extracted_date",
        "limit_results": 1000,
        "filter_empty_required": True
    }
}
```

## Testing & Development

### Test Structure

```
tests/
├── unit/                      # Unit tests for individual components
│   ├── test_proxy_rotator.py
│   ├── test_stealth_fetcher.py
│   ├── test_template_manager.py
│   └── test_data_export.py
├── integration/               # Integration tests for service interactions
│   ├── test_service_integration.py
│   ├── test_scraping_workflow.py
│   └── test_data_pipeline.py
└── e2e/                      # End-to-end tests
    ├── test_complete_workflow.py
    └── test_ui_integration.py
```

### Running Tests

#### Unit Tests
```bash
# Run all unit tests
python -m pytest tests/unit/ -v

# Run specific test file
python -m pytest tests/unit/test_proxy_rotator.py -v

# Run with coverage
python -m pytest tests/unit/ --cov=src.scrapers.proxy_rotator --cov-report=html
```

#### Integration Tests
```bash
# Run integration tests
python -m pytest tests/integration/ -v

# Run specific integration test
python -m pytest tests/integration/test_service_integration.py::test_data_service_export -v
```

#### Test Configuration
```python
# conftest.py - Test configuration
import pytest
from src.core.container import container

@pytest.fixture
def mock_container():
    """Provide isolated container for testing."""
    # Setup test container with mocked dependencies
    
@pytest.fixture
def sample_template():
    """Provide sample template for testing."""
    return {
        "name": "Test Template",
        "selectors": {
            "title": "h1::text",
            "price": ".price::text"
        }
    }

@pytest.fixture
def mock_proxies():
    """Provide test proxy list."""
    return [
        "http://test1:8080",
        "http://test2:8080"
    ]
```

### Development Workflow

#### Setting Up Development Environment
```bash
# Clone repository
git clone <repository-url>
cd ScraperV4

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run initial tests
python -m pytest tests/ -v
```

#### Code Quality Tools
```bash
# Linting
flake8 src/ tests/

# Type checking
mypy src/

# Code formatting
black src/ tests/

# Import sorting
isort src/ tests/

# Security scanning
bandit -r src/
```

#### Debug Configuration
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Component-specific debug logging
logging.getLogger('scraperv4.proxy_rotator').setLevel(logging.DEBUG)
logging.getLogger('scraperv4.stealth_fetcher').setLevel(logging.DEBUG)
logging.getLogger('scraperv4.template_scraper').setLevel(logging.DEBUG)

# Enable Eel debug mode
import eel
eel.init('web', allowed_extensions=['.js', '.html'])
eel.start('index.html', debug=True, port=8080)
```

## Troubleshooting

### Common Issues and Solutions

#### Scraping Failures

**Problem**: Jobs fail with proxy timeouts
```python
# Check proxy statistics
from src.scrapers.proxy_rotator import ProxyRotator
rotator = ProxyRotator(proxy_list)
stats = rotator.get_proxy_statistics()

if stats['active_proxies'] < len(proxy_list) * 0.5:
    # More than 50% proxies are failing
    print("Proxy issues detected:")
    for proxy_detail in stats['proxy_details']:
        if proxy_detail['status'] == 'blacklisted':
            print(f"Blacklisted: {proxy_detail['proxy']}")
```

**Solution**: 
- Verify proxy credentials and endpoints
- Increase timeout values
- Check proxy provider status
- Rotate to different proxy pools

**Problem**: Anti-bot detection blocking requests
```python
# Enable detection and get recommendations
from src.scrapers.stealth_fetcher import StealthFetcher
fetcher = StealthFetcher()
detection = fetcher.detect_anti_bot_measures(response)

if detection['detected']:
    print("Protection detected:", detection['measures'])
    print("Recommendations:", detection['recommendations'])
```

**Solution**:
- Increase request delays
- Use residential proxies
- Enable higher stealth profile
- Implement JavaScript rendering

#### Performance Issues

**Problem**: High memory usage during large jobs
```python
# Monitor job progress and memory
import psutil
import os

process = psutil.Process(os.getpid())
memory_info = process.memory_info()
print(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")

# Check job statistics
job_status = scraping_service.get_job_status(job_id)
items_per_mb = job_status['items_scraped'] / (memory_info.rss / 1024 / 1024)
print(f"Items per MB: {items_per_mb:.2f}")
```

**Solutions**:
- Implement streaming export for large datasets
- Reduce concurrent job limits
- Enable periodic memory cleanup
- Use pagination limits

#### Template Issues

**Problem**: Selectors not working on target site
```python
# Test template against URL
template_service = TemplateService()
test_results = template_service.test_template(template_id, test_url)

if test_results['validation_results']['success_rate'] < 0.8:
    print("Selector issues detected:")
    for selector, result in test_results['selector_results'].items():
        if not result['working']:
            print(f"Failed selector: {selector} - {result['error']}")
```

**Solutions**:
- Update selectors based on current site structure
- Add fallback selectors
- Use adaptive selector learning
- Implement selector validation pipeline

#### Export Problems

**Problem**: Export files are corrupted or incomplete
```python
# Validate export file
import pandas as pd
from pathlib import Path

export_path = Path("data/exports/job-uuid.xlsx")
if export_path.exists():
    try:
        df = pd.read_excel(export_path)
        print(f"Records in export: {len(df)}")
        print(f"Columns: {list(df.columns)}")
    except Exception as e:
        print(f"Export file corrupted: {e}")
```

**Solutions**:
- Check available disk space
- Verify write permissions
- Validate data structure before export
- Use streaming export for large files

### Debug Commands

#### System Health Check
```bash
# Check application status
curl http://localhost:8080/api/ping

# Check storage usage
python -c "
from src.services.data_service import DataService
ds = DataService()
print(ds.get_storage_stats())
"

# Validate templates
python -c "
from src.services.template_service import TemplateService
ts = TemplateService()
templates = ts.list_templates()
for t in templates:
    print(f'Template: {t[\"name\"]} - Valid: {t[\"is_valid\"]}')
"
```

#### Log Analysis
```bash
# View recent errors
tail -f logs/scraperv4.log | grep ERROR

# Count errors by type
grep ERROR logs/scraperv4.log | cut -d' ' -f4- | sort | uniq -c

# Monitor job progress
tail -f logs/scraperv4.log | grep "Progress:"
```

### Performance Monitoring

#### System Metrics
```python
# Monitor system performance
import psutil
import time

def monitor_performance(duration=60):
    """Monitor system performance for specified duration."""
    start_time = time.time()
    while time.time() - start_time < duration:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"CPU: {cpu_percent}% | "
              f"RAM: {memory.percent}% | "
              f"Disk: {disk.percent}%")
        
        time.sleep(5)
```

#### Application Metrics
```python
# Monitor scraping performance
def monitor_scraping_performance():
    """Monitor scraping job performance."""
    from src.services.data_service import DataService
    
    data_service = DataService()
    stats = data_service.get_storage_stats()
    
    print(f"Total jobs: {stats['total_jobs']}")
    print(f"Success rate: {stats['success_rate']:.2%}")
    print(f"Average duration: {stats['average_job_duration']}s")
    print(f"Items per second: {stats['items_per_second']:.2f}")
```

---

This technical documentation provides comprehensive coverage of ScraperV4's architecture, implementation, and usage patterns. For additional support, refer to the main README.md and INTEGRATION_REPORT.md files.