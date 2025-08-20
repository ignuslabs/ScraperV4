# Architecture Decisions

This document explains the key architectural decisions made in ScraperV4 and the reasoning behind them. Understanding these choices will help you work effectively with the framework and extend it appropriately.

## Core Architectural Principles

### 1. Service-Oriented Architecture (SOA)

**Decision**: Implement a service layer that separates business logic from infrastructure concerns.

**Rationale**:
- **Maintainability**: Clear separation of concerns makes the codebase easier to understand and modify
- **Testability**: Services can be unit tested in isolation with mock dependencies
- **Flexibility**: Services can be swapped out or modified without affecting other components
- **Scalability**: Services can be extracted into microservices if needed

**Implementation**:
```python
# Service interfaces are clean and focused
class ScrapingService(BaseService):
    def create_job(self, name: str, template_id: str, target_url: str) -> JobData
    def start_scraping_job(self, job_id: str) -> str
    def get_job_status(self, job_id: str) -> Dict[str, Any]
```

**Trade-offs**:
- **Complexity**: Additional abstraction layers vs. simpler direct implementations
- **Performance**: Slight overhead from service calls vs. direct method calls
- **Learning Curve**: Developers need to understand the service pattern

### 2. Dependency Injection Container

**Decision**: Use a custom dependency injection container instead of a heavyweight framework.

**Rationale**:
- **Loose Coupling**: Components depend on interfaces, not concrete implementations
- **Testing**: Easy to inject mock services for testing
- **Configuration**: Services can be configured and wired externally
- **Lightweight**: No external DI framework dependencies

**Implementation**:
```python
# Simple but effective DI container
container.register_singleton(ScrapingService, ScrapingServiceImpl)
container.register_factory(ProxyRotator, lambda: ProxyRotator(proxy_list))
service = container.resolve(ScrapingService)
```

**Trade-offs**:
- **Features**: Custom solution vs. full-featured DI frameworks (like dependency-injector)
- **Maturity**: Our implementation vs. battle-tested frameworks
- **Community**: Custom maintenance vs. community support

### 3. Template-Based Scraping

**Decision**: Use JSON templates to define scraping rules instead of hardcoded scrapers.

**Rationale**:
- **Reusability**: Templates can be shared and reused across different projects
- **Non-technical Users**: Business users can create templates without coding
- **Maintenance**: Changes to scraping logic don't require code deployments
- **Validation**: Templates can be validated and tested independently

**Implementation**:
```json
{
  "name": "E-commerce Product",
  "selectors": {
    "title": "h1.product-title::text",
    "price": ".price-current::text",
    "images": "img.product-image::attr(src)"
  },
  "pagination": {
    "next_page_selector": ".pagination .next",
    "max_pages": 50
  }
}
```

**Trade-offs**:
- **Flexibility**: Template constraints vs. unlimited programmatic control
- **Performance**: Template parsing overhead vs. compiled scrapers
- **Complexity**: Template engine complexity vs. simple scraping logic

### 4. Asynchronous Processing

**Decision**: Use async/await for I/O operations and job processing.

**Rationale**:
- **Performance**: Non-blocking I/O allows handling many concurrent requests
- **Resource Efficiency**: Better CPU and memory utilization
- **Scalability**: Can handle more concurrent scraping jobs
- **Responsiveness**: UI remains responsive during long-running operations

**Implementation**:
```python
async def scrape_multiple_pages(self, urls: List[str]) -> List[Dict]:
    tasks = [self._scrape_single_page(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

**Trade-offs**:
- **Complexity**: Async programming complexity vs. simple synchronous code
- **Debugging**: Async stack traces can be harder to follow
- **Libraries**: Not all libraries support async operations

### 5. EEL Framework for Web Interface

**Decision**: Use EEL to bridge Python backend with HTML/JavaScript frontend.

**Rationale**:
- **Simplicity**: Easier than building separate API and frontend
- **Real-time Communication**: Built-in WebSocket support for live updates
- **Local Deployment**: Perfect for desktop-like applications
- **Python Integration**: Direct access to Python functions from JavaScript

**Implementation**:
```python
@eel.expose
def start_scraping_job(job_data):
    service = container.resolve(ScrapingService)
    return service.create_and_start_job(job_data)
```

**Trade-offs**:
- **Scalability**: EEL is designed for single-user applications
- **Deployment**: Less suitable for multi-user web applications
- **Modern Frameworks**: Missing features compared to React/Vue/Angular

### 6. File-Based Data Storage

**Decision**: Use JSON files for job storage instead of a database.

**Rationale**:
- **Simplicity**: No database setup or maintenance required
- **Portability**: Data files can be easily backed up and moved
- **Human Readable**: JSON files can be inspected and modified manually
- **Version Control**: Data can be tracked in version control if needed

**Implementation**:
```python
# Jobs stored as individual JSON files
data/jobs/
├── job-12345.json
├── job-67890.json
└── job-abcde.json
```

**Trade-offs**:
- **Performance**: File I/O vs. database queries for large datasets
- **Concurrency**: File locking issues vs. database transactions
- **Querying**: Limited search capabilities vs. SQL queries
- **ACID**: No transaction guarantees vs. database ACID properties

### 7. Scrapling Integration

**Decision**: Build on top of Scrapling library for core scraping functionality.

**Rationale**:
- **Proven Technology**: Scrapling has advanced stealth and anti-detection features
- **Development Speed**: Don't reinvent web scraping fundamentals
- **Maintenance**: Benefit from Scrapling's ongoing development and bug fixes
- **Features**: Advanced features like proxy rotation and CAPTCHA handling

**Implementation**:
```python
from scrapling.fetchers import StealthyFetcher
# Wrap Scrapling with our own abstractions
class StealthFetcher(BaseScraper):
    def __init__(self):
        self.fetcher = StealthyFetcher()
```

**Trade-offs**:
- **Dependency**: External dependency vs. full control
- **Compatibility**: Must stay compatible with Scrapling updates
- **Customization**: Limited by Scrapling's capabilities and design

### 8. Modular Scraper Design

**Decision**: Separate fetching, parsing, and processing into distinct components.

**Rationale**:
- **Single Responsibility**: Each component has one clear purpose
- **Composability**: Components can be mixed and matched as needed
- **Testing**: Each component can be tested independently
- **Extensibility**: New components can be added without affecting others

**Implementation**:
```python
# Clear separation of concerns
class StealthFetcher(BaseScraper):     # Handles HTTP requests
class TemplateScraper(BaseScraper):    # Handles data extraction
class ProxyRotator:                    # Handles proxy management
```

**Trade-offs**:
- **Overhead**: Multiple objects vs. monolithic scraper
- **Coordination**: Need to coordinate between components
- **Complexity**: More moving parts vs. simple single-class design

## Design Patterns Used

### 1. Strategy Pattern
Used for different scraping strategies (stealth, template-based, etc.):
```python
class BaseScraper(ABC):
    @abstractmethod
    def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        pass
```

### 2. Factory Pattern
Used in the service container for creating service instances:
```python
def register_factory(self, interface: Type[T], factory: Callable[[], T]):
    self._factories[interface] = factory
```

### 3. Observer Pattern
Used for job progress notifications through EEL:
```python
def notify_progress(self, job_id: str, progress: int):
    eel.update_job_progress(job_id, progress)
```

### 4. Template Method Pattern
Used in base service class for common service operations:
```python
class BaseService:
    def execute_operation(self):
        self.validate_input()      # Template method
        self.perform_operation()   # Implemented by subclasses
        self.log_operation()       # Template method
```

## Alternative Approaches Considered

### 1. Database vs. File Storage
**Considered**: PostgreSQL, SQLite, MongoDB
**Chosen**: JSON files
**Reason**: Simplicity outweighed performance benefits for the target use case

### 2. FastAPI vs. EEL
**Considered**: FastAPI + React frontend
**Chosen**: EEL
**Reason**: Simpler deployment and better integration for desktop-like application

### 3. Celery vs. asyncio
**Considered**: Celery for distributed task processing
**Chosen**: asyncio
**Reason**: Simpler setup and sufficient for single-machine deployments

### 4. Configuration Management
**Considered**: YAML, TOML, environment variables only
**Chosen**: Pydantic with environment variable support
**Reason**: Type safety and validation while maintaining flexibility

## Evolution Strategy

### Short-term (Current)
- File-based storage with JSON
- Single-machine deployment
- EEL-based web interface
- Manual proxy configuration

### Medium-term (Possible)
- Optional database backend
- Distributed job processing
- REST API for external integration
- Automatic proxy sourcing

### Long-term (Future)
- Cloud-native deployment
- Machine learning for anti-detection
- Visual template builder
- Multi-tenant support

## Conclusion

ScraperV4's architecture prioritizes simplicity and maintainability while providing enterprise-grade features. The modular design allows for gradual complexity increases as needs evolve. Each architectural decision represents a careful balance between current requirements and future extensibility.

The service-oriented approach provides a clean foundation that can support both simple use cases and complex enterprise deployments. The template-based system democratizes web scraping while the async processing ensures performance at scale.

These decisions create a framework that is both approachable for newcomers and powerful enough for advanced use cases, supporting ScraperV4's goal of being the go-to solution for web scraping across different skill levels and organizational needs.