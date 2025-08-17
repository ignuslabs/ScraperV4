# Phase 1B: Project Structure - ScraperV4 Architecture Foundation

## Objective
Establish a scalable, maintainable project architecture for ScraperV4 with proper separation of concerns, dependency injection patterns, and modular component organization. Create the foundational structure that supports template-based scraping, service container architecture, and seamless Eel integration.

## Context
Building upon the environment setup from Phase 1A, this phase creates the core architectural foundation:
- **Service Container**: Dependency injection system for loose coupling
- **Template System**: Self-healing scraping configuration management  
- **File Storage Layer**: JSON-based data persistence for jobs, templates, and results
- **Scraper Framework**: Scrapling integration with stealth capabilities
- **Eel Bridge**: Python-JavaScript communication layer
- **Configuration Management**: Environment-based settings with validation

## Architecture Overview
```
ScraperV4/
├── src/                    # Core application code
│   ├── core/              # Core services and dependency injection
│   ├── data/              # File-based data storage managers
│   ├── services/          # Business logic services
│   ├── scrapers/          # Scrapling-based scraper implementations
│   ├── templates/         # Self-healing scraper templates
│   ├── utils/             # Utility functions and helpers
│   └── web/               # Eel web interface integration
├── web/                   # Frontend assets (HTML, CSS, JS)
├── tests/                 # Comprehensive test suite
├── data/                  # Data storage and exports
├── logs/                  # Application logging
└── templates/            # Scraping template configurations
```

## Implementation Steps

### 1. Core Service Container Architecture

Create `src/core/container.py`:
```python
"""Service container for dependency injection in ScraperV4."""

from typing import TypeVar, Type, Dict, Any, Optional, Callable
import threading
from functools import lru_cache

T = TypeVar('T')

class ServiceContainer:
    """Dependency injection container for managing service instances."""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
        self._lock = threading.Lock()
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a singleton service."""
        with self._lock:
            self._services[interface] = implementation
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register a factory function for service creation."""
        with self._lock:
            self._factories[interface] = factory
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Register a pre-created instance."""
        with self._lock:
            self._singletons[interface] = instance
    
    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service instance."""
        with self._lock:
            # Check for existing singleton
            if interface in self._singletons:
                return self._singletons[interface]
            
            # Check for factory
            if interface in self._factories:
                instance = self._factories[interface]()
                self._singletons[interface] = instance
                return instance
            
            # Check for registered service
            if interface in self._services:
                implementation = self._services[interface]
                instance = implementation()
                self._singletons[interface] = instance
                return instance
            
            raise ValueError(f"Service {interface} not registered")
    
    def clear(self) -> None:
        """Clear all registered services (mainly for testing)."""
        with self._lock:
            self._services.clear()
            self._factories.clear()
            self._singletons.clear()

# Global container instance
container = ServiceContainer()
```

Create `src/core/config.py`:
```python
"""Configuration management for ScraperV4."""

import os
from typing import Optional, List
from pathlib import Path
from pydantic import BaseSettings, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class StorageConfig(BaseSettings):
    """File storage configuration settings."""
    data_folder: str = "data"
    jobs_folder: str = "data/jobs"
    results_folder: str = "data/results"
    templates_folder: str = "templates"
    
    class Config:
        env_prefix = "STORAGE_"

class ScraplingConfig(BaseSettings):
    """Scrapling scraper configuration."""
    stealth_mode: bool = True
    user_agent: str = "ScraperV4/1.0"
    timeout: int = 30
    max_retries: int = 3
    delay_range: tuple = (1, 3)
    
    class Config:
        env_prefix = "SCRAPLING_"
    
    @validator('delay_range', pre=True)
    def parse_delay_range(cls, v):
        if isinstance(v, str):
            parts = v.split(',')
            return (int(parts[0]), int(parts[1]))
        return v

class EelConfig(BaseSettings):
    """Eel web interface configuration."""
    port: int = 8080
    debug: bool = True
    web_folder: str = "web"
    allowed_extensions: List[str] = ['.html', '.css', '.js', '.png', '.jpg', '.gif']
    
    class Config:
        env_prefix = "EEL_"

class LoggingConfig(BaseSettings):
    """Logging configuration."""
    level: str = "INFO"
    file: str = "logs/scraperv4.log"
    max_bytes: int = 10_000_000  # 10MB
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_prefix = "LOG_"

class AppConfig(BaseSettings):
    """Main application configuration."""
    app_name: str = "ScraperV4"
    version: str = "1.0.0"
    data_folder: str = "data"
    templates_folder: str = "templates"
    
    # Sub-configurations
    storage: StorageConfig = StorageConfig()
    scrapling: ScraplingConfig = ScraplingConfig()
    eel: EelConfig = EelConfig()
    logging: LoggingConfig = LoggingConfig()
    
    @validator('data_folder', 'templates_folder')
    def ensure_folder_exists(cls, v):
        Path(v).mkdir(parents=True, exist_ok=True)
        return v

# Global configuration instance
config = AppConfig()
```

### 2. File-Based Data Storage System

Create `src/data/__init__.py`:
```python
"""File-based data storage for ScraperV4."""

from .job_manager import JobManager
from .template_manager import FileTemplateManager
from .result_storage import ResultStorage

__all__ = ['JobManager', 'FileTemplateManager', 'ResultStorage']
```

Create `src/data/job_manager.py`:
```python
"""Job management with file-based storage."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.core.config import config

class JobManager:
    """Manages scraping jobs using file storage."""
    
    def __init__(self):
        self.jobs_dir = Path(config.data_folder) / "jobs"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
    
    def create_job(self, name: str, template_name: str, target_url: str,
                   job_config: Optional[Dict[str, Any]] = None,
                   parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new scraping job."""
        job_id = str(uuid.uuid4())
        job_data = {
            "id": job_id,
            "name": name,
            "template_name": template_name,
            "target_url": target_url,
            "config": job_config or {},
            "parameters": parameters or {},
            "status": "pending",
            "progress": 0,
            "items_scraped": 0,
            "items_failed": 0,
            "created_at": datetime.utcnow().isoformat(),
            "started_at": None,
            "completed_at": None,
            "error_message": None,
            "retry_count": 0
        }
        
        job_file = self.jobs_dir / f"{job_id}.json"
        with open(job_file, 'w') as f:
            json.dump(job_data, f, indent=2)
        
        return job_data
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID."""
        job_file = self.jobs_dir / f"{job_id}.json"
        if job_file.exists():
            with open(job_file, 'r') as f:
                return json.load(f)
        return None
    
    def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """Update job data."""
        job_data = self.get_job(job_id)
        if job_data:
            job_data.update(updates)
            job_file = self.jobs_dir / f"{job_id}.json"
            with open(job_file, 'w') as f:
                json.dump(job_data, f, indent=2)
            return True
        return False
    
    def list_jobs(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all jobs with optional status filter."""
        jobs = []
        for job_file in self.jobs_dir.glob("*.json"):
            try:
                with open(job_file, 'r') as f:
                    job_data = json.load(f)
                if not status or job_data.get('status') == status:
                    jobs.append(job_data)
            except Exception:
                continue
        
        return sorted(jobs, key=lambda x: x.get('created_at', ''), reverse=True)
```

### 3. Service Layer Architecture

Create `src/services/__init__.py`:
```python
"""Service layer for ScraperV4 business logic."""

from .scraping_service import ScrapingService
from .template_service import TemplateService
from .data_service import DataService

__all__ = ['ScrapingService', 'TemplateService', 'DataService']
```

Create `src/services/base_service.py`:
```python
"""Base service class with common functionality."""

from typing import Optional
from src.data.job_manager import JobManager
from src.data.template_manager import FileTemplateManager
from src.data.result_storage import ResultStorage
from src.core.container import container

class BaseService:
    """Base service with file storage management."""
    
    def __init__(self):
        self.job_manager = JobManager()
        self.template_manager = FileTemplateManager()
        self.result_storage = ResultStorage()
```

### 4. Scrapling Integration Framework

Create `src/scrapers/__init__.py`:
```python
"""Scrapling-based scraper framework."""

from .base_scraper import BaseScraper
from .template_scraper import TemplateScraper
from .stealth_fetcher import StealthFetcher

__all__ = ['BaseScraper', 'TemplateScraper', 'StealthFetcher']
```

Create `src/scrapers/base_scraper.py`:
```python
"""Base scraper class with Scrapling integration."""

import time
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from scrapling import Fetcher
from src.core.config import config
from src.core.container import container

class BaseScraper(ABC):
    """Base scraper class with common functionality."""
    
    def __init__(self):
        self.fetcher = self._create_fetcher()
        self.config = config.scrapling
    
    def _create_fetcher(self) -> Fetcher:
        """Create configured Scrapling fetcher."""
        fetcher_config = {
            'stealth': self.config.stealth_mode,
            'timeout': self.config.timeout,
            'user_agent': self.config.user_agent,
        }
        return Fetcher(**fetcher_config)
    
    @abstractmethod
    def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """Abstract method for scraping implementation."""
        pass
    
    def scrape_multiple(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Scrape multiple URLs with delay between requests."""
        results = []
        for i, url in enumerate(urls):
            try:
                result = self.scrape(url, **kwargs)
                results.append(result)
                
                # Add delay between requests (except for last URL)
                if i < len(urls) - 1:
                    delay = self._calculate_delay()
                    time.sleep(delay)
                    
            except Exception as e:
                results.append({
                    'url': url,
                    'error': str(e),
                    'status': 'failed'
                })
        
        return results
    
    def _calculate_delay(self) -> float:
        """Calculate delay between requests."""
        import random
        min_delay, max_delay = self.config.delay_range
        return random.uniform(min_delay, max_delay)
    
    def validate_response(self, response) -> bool:
        """Validate scraping response."""
        return response is not None and hasattr(response, 'content')
```

### 5. Template System Foundation

Create `src/templates/__init__.py`:
```python
"""Self-healing template system for ScraperV4."""

from .template_manager import TemplateManager
from .template_validator import TemplateValidator
from .adaptive_selector import AdaptiveSelector

__all__ = ['TemplateManager', 'TemplateValidator', 'AdaptiveSelector']
```

Create `src/templates/template_manager.py`:
```python
"""Template management system with self-healing capabilities."""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from src.core.config import config

class TemplateManager:
    """Manages scraping templates with self-healing capabilities."""
    
    def __init__(self):
        self.templates_dir = Path(config.templates_folder)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._templates_cache: Dict[str, Dict[str, Any]] = {}
    
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """Load template from file or cache."""
        if template_name in self._templates_cache:
            return self._templates_cache[template_name]
        
        template_path = self.templates_dir / f"{template_name}.json"
        if not template_path.exists():
            raise FileNotFoundError(f"Template {template_name} not found")
        
        with open(template_path, 'r') as f:
            template = json.load(f)
        
        self._templates_cache[template_name] = template
        return template
    
    def save_template(self, template_name: str, template_data: Dict[str, Any]) -> None:
        """Save template to file and update cache."""
        template_path = self.templates_dir / f"{template_name}.json"
        
        with open(template_path, 'w') as f:
            json.dump(template_data, f, indent=2)
        
        self._templates_cache[template_name] = template_data
    
    def list_templates(self) -> List[str]:
        """List all available templates."""
        return [f.stem for f in self.templates_dir.glob("*.json")]
    
    def create_default_template(self, name: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Create a default template structure."""
        template = {
            "name": name,
            "version": "1.0.0",
            "selectors": selectors,
            "validation_rules": {},
            "adaptive_selectors": True,
            "fallback_selectors": {},
            "post_processing": []
        }
        
        self.save_template(name, template)
        return template
```

### 6. Eel Web Interface Integration

Create `src/web/__init__.py`:
```python
"""Eel web interface integration for ScraperV4."""

from .eel_app import EelApp
from .api_routes import register_api_routes

__all__ = ['EelApp', 'register_api_routes']
```

Create `src/web/eel_app.py`:
```python
"""Eel application wrapper for ScraperV4."""

import eel
from pathlib import Path
from src.core.config import config
from src.core.container import container

class EelApp:
    """Eel application wrapper with ScraperV4 integration."""
    
    def __init__(self):
        self.config = config.eel
        self.web_folder = Path(self.config.web_folder)
        self._setup_eel()
    
    def _setup_eel(self):
        """Initialize Eel with configuration."""
        eel.init(str(self.web_folder))
    
    def start(self, start_url: str = "index.html", **kwargs):
        """Start the Eel application."""
        eel_kwargs = {
            'mode': 'chrome',
            'port': self.config.port,
            'close_callback': self._on_close,
            **kwargs
        }
        
        if self.config.debug:
            eel_kwargs['debug'] = True
        
        eel.start(start_url, **eel_kwargs)
    
    def _on_close(self, page, sockets):
        """Handle application close event."""
        print("Application closed")
    
    @staticmethod
    def expose(func):
        """Decorator to expose Python functions to JavaScript."""
        return eel.expose(func)
```

### 7. Utility Functions and Helpers

Create `src/utils/__init__.py`:
```python
"""Utility functions and helpers for ScraperV4."""

from .logging_utils import setup_logging, get_logger
from .data_utils import export_to_csv, export_to_json, export_to_excel
from .validation_utils import validate_url, validate_selector

__all__ = [
    'setup_logging', 'get_logger',
    'export_to_csv', 'export_to_json', 'export_to_excel',
    'validate_url', 'validate_selector'
]
```

Create `src/utils/logging_utils.py`:
```python
"""Logging utilities for ScraperV4."""

import logging
import logging.handlers
from pathlib import Path
from src.core.config import config

def setup_logging() -> None:
    """Set up logging configuration."""
    log_config = config.logging
    
    # Create logs directory
    log_path = Path(log_config.file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_config.level),
        format=log_config.format,
        handlers=[
            logging.handlers.RotatingFileHandler(
                log_config.file,
                maxBytes=log_config.max_bytes,
                backupCount=log_config.backup_count
            ),
            logging.StreamHandler()
        ]
    )

def get_logger(name: str) -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(name)
```

### 8. Application Entry Point

Create `src/main.py`:
```python
"""Main application entry point for ScraperV4."""

import sys
from pathlib import Path
from src.core.config import config
from src.core.container import container
from src.utils.logging_utils import setup_logging, get_logger
from src.web.eel_app import EelApp
from src.web.api_routes import register_api_routes

def setup_application():
    """Set up application components."""
    # Set up logging
    setup_logging()
    logger = get_logger(__name__)
    logger.info(f"Starting {config.app_name} v{config.version}")
    
    # Register services in container
    from src.services.scraping_service import ScrapingService
    from src.services.template_service import TemplateService
    from src.services.data_service import DataService
    
    container.register_singleton(ScrapingService, ScrapingService)
    container.register_singleton(TemplateService, TemplateService)
    container.register_singleton(DataService, DataService)
    
    logger.info("Application setup completed")

def main():
    """Main application entry point."""
    try:
        setup_application()
        
        # Create and start Eel application
        app = EelApp()
        register_api_routes()
        
        print(f"Starting {config.app_name} on http://localhost:{config.eel.port}")
        app.start()
        
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Application failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Validation Criteria

### Success Metrics
1. ✅ Service container properly manages dependencies
2. ✅ File storage system creates required directories and manages data
3. ✅ Configuration system loads environment variables
4. ✅ Template manager can create and load templates
5. ✅ Scrapling integration initializes correctly
6. ✅ Eel application structure is ready for web interface
7. ✅ Logging system writes to both file and console
8. ✅ All imports resolve without circular dependencies

### Validation Commands
```bash
# Test configuration loading
python -c "from src.core.config import config; print(f'App: {config.app_name}')"

# Test service container
python -c "from src.core.container import container; print('Container initialized')"

# Test data storage
python -c "from src.data import JobManager, FileTemplateManager; print('Storage systems imported')"

# Test Scrapling integration
python -c "from src.scrapers.base_scraper import BaseScraper; print('Scrapers ready')"

# Run main application (should not error on startup)
python src/main.py --help
```

### File Structure Validation
```bash
# Check all required files exist
find src -name "*.py" | wc -l  # Should be 15+ files
ls src/core/container.py src/core/config.py src/models/base.py
ls src/services/__init__.py src/scrapers/base_scraper.py
```

## Troubleshooting Guide

### Import Errors
```bash
# If circular imports occur, check dependency order
python -c "import sys; sys.path.insert(0, 'src'); import core.container"
```

### File Storage Issues
```bash
# Test data storage setup
python -c "from src.data.job_manager import JobManager; jm = JobManager(); print('Job manager initialized')"
```

### Configuration Problems
- Verify `.env` file has all required variables
- Check `pyproject.toml` syntax with: `python -c "import toml; toml.load('pyproject.toml')"`

### Service Container Issues
- Ensure services implement proper interfaces
- Check for missing `__init__` methods in service classes

## Next Steps
After successful completion:
1. Proceed to **Phase 1C: Eel Application Architecture** to build the web interface
2. All foundational services are registered and available
3. File-based storage system is ready for data management
4. Template system is prepared for scraping configurations

## File Deliverables
- `src/core/container.py` - Dependency injection container
- `src/core/config.py` - Configuration management system  
- `src/data/` - File-based storage system for jobs, templates, and results
- `src/services/` - Service layer foundation
- `src/scrapers/` - Scrapling integration framework
- `src/templates/` - Self-healing template system
- `src/web/` - Eel application wrapper
- `src/utils/` - Utility functions and helpers
- `src/main.py` - Application entry point