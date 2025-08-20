# Service Container and Dependency Injection

This document explains ScraperV4's dependency injection architecture, the service container pattern, and how it enables maintainable, testable, and flexible code. Understanding this pattern is crucial for extending ScraperV4 and building robust applications.

## The Dependency Problem

### Traditional Tightly Coupled Design

Without dependency injection, components are tightly coupled:

```python
# Tightly coupled - hard to test and modify
class ScrapingService:
    def __init__(self):
        self.template_manager = TemplateManager()  # Hard dependency
        self.job_manager = JobManager()            # Hard dependency
        self.proxy_rotator = ProxyRotator([        # Hard-coded config
            "proxy1.example.com:8080",
            "proxy2.example.com:8080"
        ])
    
    def create_job(self, template_id: str):
        # Cannot easily mock these dependencies for testing
        template = self.template_manager.load_template(template_id)
        job = self.job_manager.create_job(template)
        return job
```

**Problems with Tight Coupling**:
- **Hard to Test**: Cannot easily mock dependencies
- **Inflexible**: Cannot change implementations without code changes
- **Circular Dependencies**: Services can depend on each other
- **Configuration Issues**: Hard-coded configuration scattered throughout code
- **Maintenance Burden**: Changes ripple through multiple classes

### Dependency Injection Solution

Dependency injection inverts control by providing dependencies from outside:

```python
# Loosely coupled - flexible and testable
class ScrapingService:
    def __init__(self, template_manager: TemplateManager, 
                 job_manager: JobManager, 
                 proxy_rotator: ProxyRotator):
        self.template_manager = template_manager  # Injected dependency
        self.job_manager = job_manager            # Injected dependency  
        self.proxy_rotator = proxy_rotator        # Injected dependency
    
    def create_job(self, template_id: str):
        # Dependencies are provided by caller
        template = self.template_manager.load_template(template_id)
        job = self.job_manager.create_job(template)
        return job
```

**Benefits of Dependency Injection**:
- **Testability**: Easy to inject mock objects for testing
- **Flexibility**: Can swap implementations without code changes
- **Configuration**: Centralized dependency configuration
- **Modularity**: Clear interfaces between components
- **Maintainability**: Changes are isolated to specific areas

## ScraperV4's Service Container

### Container Architecture

ScraperV4 implements a lightweight service container for managing dependencies:

```python
from typing import TypeVar, Type, Dict, Any, Callable
import threading

T = TypeVar('T')

class ServiceContainer:
    """Dependency injection container for managing service instances."""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}        # Registered service types
        self._factories: Dict[Type, Callable] = {}  # Factory functions
        self._singletons: Dict[Type, Any] = {}      # Singleton instances
        self._lock = threading.Lock()               # Thread safety
    
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
```

### Service Registration Patterns

ScraperV4 supports multiple registration patterns:

#### 1. Singleton Registration

Most services are registered as singletons:

```python
# Register service types
container.register_singleton(ScrapingService, ScrapingServiceImpl)
container.register_singleton(DataService, DataServiceImpl)
container.register_singleton(TemplateService, TemplateServiceImpl)

# Usage - same instance returned every time
service1 = container.resolve(ScrapingService)
service2 = container.resolve(ScrapingService)
assert service1 is service2  # Same instance
```

#### 2. Factory Registration

For services that need custom initialization:

```python
def create_proxy_rotator():
    """Factory function for creating proxy rotator."""
    proxy_list = load_proxy_configuration()
    return ProxyRotator(proxy_list)

def create_stealth_fetcher():
    """Factory function for creating stealth fetcher."""
    config = load_stealth_configuration()
    return StealthFetcher(config)

# Register factories
container.register_factory(ProxyRotator, create_proxy_rotator)
container.register_factory(StealthFetcher, create_stealth_fetcher)

# Usage - factory called each time (but result cached as singleton)
rotator = container.resolve(ProxyRotator)
```

#### 3. Instance Registration

For pre-configured instances:

```python
# Create and configure instance
config = AppConfig()
config.load_from_file('config.json')

# Register pre-configured instance
container.register_instance(AppConfig, config)

# Usage
app_config = container.resolve(AppConfig)
```

### Service Configuration and Bootstrap

Services are configured and registered during application startup:

```python
def configure_services(container: ServiceContainer) -> None:
    """Configure all application services."""
    
    # Core configuration
    config = AppConfig()
    container.register_instance(AppConfig, config)
    
    # Data layer services
    container.register_singleton(JobManager, FileJobManager)
    container.register_singleton(ResultStorage, FileResultStorage)
    container.register_singleton(TemplateManager, JsonTemplateManager)
    
    # Business logic services
    container.register_singleton(ScrapingService, ScrapingServiceImpl)
    container.register_singleton(DataService, DataServiceImpl)
    container.register_singleton(TemplateService, TemplateServiceImpl)
    
    # Infrastructure services
    container.register_factory(ProxyRotator, lambda: create_proxy_rotator(config))
    container.register_factory(StealthFetcher, lambda: create_stealth_fetcher(config))
    
    # Scrapers
    container.register_factory(TemplateScraper, create_template_scraper)

def create_proxy_rotator(config: AppConfig) -> ProxyRotator:
    """Create proxy rotator with configuration."""
    proxy_list = config.get_proxy_list()
    return ProxyRotator(proxy_list)

def create_stealth_fetcher(config: AppConfig) -> StealthFetcher:
    """Create stealth fetcher with configuration."""
    stealth_config = config.get_stealth_config()
    return StealthFetcher(stealth_config)

def create_template_scraper() -> TemplateScraper:
    """Create template scraper with dependencies."""
    # Resolve dependencies from container
    template_manager = container.resolve(TemplateManager)
    return TemplateScraper(template_manager)

# Application startup
container = ServiceContainer()
configure_services(container)
```

## Service Interfaces and Implementations

### Abstract Base Classes

ScraperV4 uses abstract base classes to define service contracts:

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseService(ABC):
    """Base class for all services."""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the service."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup service resources."""
        pass

class TemplateService(BaseService):
    """Abstract template service interface."""
    
    @abstractmethod
    def create_template(self, template_data: Dict[str, Any]) -> str:
        """Create a new template."""
        pass
    
    @abstractmethod
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template by ID."""
        pass
    
    @abstractmethod
    def update_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """Update existing template."""
        pass
    
    @abstractmethod
    def delete_template(self, template_id: str) -> bool:
        """Delete template."""
        pass
    
    @abstractmethod
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all templates."""
        pass
    
    @abstractmethod
    def test_template(self, template_id: str, test_url: str) -> Dict[str, Any]:
        """Test template against URL."""
        pass
```

### Concrete Implementations

Services implement the abstract interfaces:

```python
class TemplateServiceImpl(TemplateService):
    """File-based template service implementation."""
    
    def __init__(self, template_manager: TemplateManager, 
                 template_validator: TemplateValidator):
        self.template_manager = template_manager
        self.template_validator = template_validator
        self.initialized = False
    
    def initialize(self) -> None:
        """Initialize the template service."""
        if not self.initialized:
            self.template_manager.initialize()
            self.initialized = True
    
    def cleanup(self) -> None:
        """Cleanup template service resources."""
        if self.initialized:
            self.template_manager.cleanup()
            self.initialized = False
    
    def create_template(self, template_data: Dict[str, Any]) -> str:
        """Create a new template."""
        # Validate template data
        validation_result = self.template_validator.validate(template_data)
        if not validation_result.valid:
            raise ValidationError(f"Invalid template: {validation_result.errors}")
        
        # Create template
        template_id = self.template_manager.create_template(template_data)
        
        return template_id
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template by ID."""
        return self.template_manager.load_template(template_id)
    
    def test_template(self, template_id: str, test_url: str) -> Dict[str, Any]:
        """Test template against URL."""
        template = self.get_template(template_id)
        if not template:
            raise TemplateNotFound(f"Template {template_id} not found")
        
        # Create template scraper and test
        scraper = TemplateScraper(template)
        result = scraper.scrape(test_url)
        
        return result
```

## Service Lifecycle Management

### Service Initialization

Services have a managed lifecycle:

```python
class ServiceLifecycleManager:
    """Manages service lifecycle events."""
    
    def __init__(self, container: ServiceContainer):
        self.container = container
        self.initialized_services = set()
    
    def initialize_all_services(self) -> None:
        """Initialize all registered services."""
        # Get all registered service types
        service_types = list(self.container._services.keys())
        service_types.extend(self.container._factories.keys())
        
        for service_type in service_types:
            self.initialize_service(service_type)
    
    def initialize_service(self, service_type: Type) -> None:
        """Initialize a specific service type."""
        if service_type in self.initialized_services:
            return
        
        try:
            # Resolve service instance
            service = self.container.resolve(service_type)
            
            # Initialize if it's a BaseService
            if isinstance(service, BaseService):
                service.initialize()
            
            self.initialized_services.add(service_type)
            
        except Exception as e:
            logger.error(f"Failed to initialize service {service_type}: {e}")
            raise
    
    def cleanup_all_services(self) -> None:
        """Cleanup all initialized services."""
        for service_type in list(self.initialized_services):
            self.cleanup_service(service_type)
    
    def cleanup_service(self, service_type: Type) -> None:
        """Cleanup a specific service."""
        if service_type not in self.initialized_services:
            return
        
        try:
            service = self.container.resolve(service_type)
            
            if isinstance(service, BaseService):
                service.cleanup()
            
            self.initialized_services.remove(service_type)
            
        except Exception as e:
            logger.error(f"Failed to cleanup service {service_type}: {e}")
```

### Application Startup and Shutdown

Services are managed during application lifecycle:

```python
class Application:
    """Main application class with service management."""
    
    def __init__(self):
        self.container = ServiceContainer()
        self.lifecycle_manager = ServiceLifecycleManager(self.container)
        self.running = False
    
    def start(self) -> None:
        """Start the application."""
        try:
            # Configure services
            configure_services(self.container)
            
            # Initialize all services
            self.lifecycle_manager.initialize_all_services()
            
            # Start EEL interface
            self.start_eel_interface()
            
            self.running = True
            logger.info("Application started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            self.shutdown()
            raise
    
    def shutdown(self) -> None:
        """Shutdown the application."""
        if self.running:
            logger.info("Shutting down application...")
            
            # Cleanup all services
            self.lifecycle_manager.cleanup_all_services()
            
            # Clear container
            self.container.clear()
            
            self.running = False
            logger.info("Application shutdown complete")
    
    def start_eel_interface(self) -> None:
        """Start EEL web interface."""
        # Expose EEL functions that use the container
        self.register_eel_functions()
        
        # Start EEL
        config = self.container.resolve(AppConfig)
        eel.start('index.html', 
                 port=config.eel.port, 
                 debug=config.eel.debug)
    
    def register_eel_functions(self) -> None:
        """Register EEL-exposed functions."""
        
        @eel.expose
        def start_scraping_job(job_data):
            service = self.container.resolve(ScrapingService)
            return service.create_and_start_job(job_data)
        
        @eel.expose
        def get_job_status(job_id):
            service = self.container.resolve(ScrapingService)
            return service.get_job_status(job_id)
        
        @eel.expose
        def create_template(template_data):
            service = self.container.resolve(TemplateService)
            return service.create_template(template_data)
```

## Testing with Dependency Injection

### Mock Services for Testing

Dependency injection makes testing much easier:

```python
import pytest
from unittest.mock import Mock, MagicMock

class TestScrapingService:
    """Test suite for ScrapingService."""
    
    def setup_method(self):
        """Setup test environment."""
        # Create mock dependencies
        self.mock_template_manager = Mock(spec=TemplateManager)
        self.mock_job_manager = Mock(spec=JobManager)
        self.mock_proxy_rotator = Mock(spec=ProxyRotator)
        
        # Create service with mocked dependencies
        self.service = ScrapingServiceImpl(
            template_manager=self.mock_template_manager,
            job_manager=self.mock_job_manager,
            proxy_rotator=self.mock_proxy_rotator
        )
    
    def test_create_job_success(self):
        """Test successful job creation."""
        # Setup mocks
        template_data = {'name': 'test', 'selectors': {}}
        self.mock_template_manager.load_template.return_value = template_data
        self.mock_job_manager.create_job.return_value = {'id': 'job-123'}
        
        # Execute
        result = self.service.create_job('template-456', 'http://example.com')
        
        # Verify
        assert result['id'] == 'job-123'
        self.mock_template_manager.load_template.assert_called_once_with('template-456')
        self.mock_job_manager.create_job.assert_called_once()
    
    def test_create_job_template_not_found(self):
        """Test job creation with missing template."""
        # Setup mock to return None
        self.mock_template_manager.load_template.return_value = None
        
        # Execute and verify exception
        with pytest.raises(TemplateNotFound):
            self.service.create_job('missing-template', 'http://example.com')

class TestContainerIntegration:
    """Integration tests using the service container."""
    
    def setup_method(self):
        """Setup test container."""
        self.container = ServiceContainer()
        self.configure_test_services()
    
    def configure_test_services(self):
        """Configure services for testing."""
        # Use mock implementations
        self.container.register_instance(TemplateManager, Mock(spec=TemplateManager))
        self.container.register_instance(JobManager, Mock(spec=JobManager))
        self.container.register_instance(ProxyRotator, Mock(spec=ProxyRotator))
        
        # Register real service implementations
        self.container.register_singleton(ScrapingService, ScrapingServiceImpl)
    
    def test_service_resolution(self):
        """Test that services can be resolved from container."""
        service = self.container.resolve(ScrapingService)
        assert isinstance(service, ScrapingServiceImpl)
    
    def test_singleton_behavior(self):
        """Test that singletons return same instance."""
        service1 = self.container.resolve(ScrapingService)
        service2 = self.container.resolve(ScrapingService)
        assert service1 is service2
```

### Test Configuration

Separate configuration for test environments:

```python
def configure_test_services(container: ServiceContainer) -> None:
    """Configure services for testing environment."""
    
    # Test configuration
    test_config = AppConfig()
    test_config.data_folder = "test_data"
    test_config.templates_folder = "test_templates"
    container.register_instance(AppConfig, test_config)
    
    # Use in-memory implementations for testing
    container.register_singleton(JobManager, InMemoryJobManager)
    container.register_singleton(ResultStorage, InMemoryResultStorage)
    container.register_singleton(TemplateManager, InMemoryTemplateManager)
    
    # Mock external dependencies
    container.register_instance(ProxyRotator, Mock(spec=ProxyRotator))
    container.register_instance(StealthFetcher, Mock(spec=StealthFetcher))
    
    # Real service implementations
    container.register_singleton(ScrapingService, ScrapingServiceImpl)
    container.register_singleton(DataService, DataServiceImpl)
    container.register_singleton(TemplateService, TemplateServiceImpl)

@pytest.fixture
def test_container():
    """Pytest fixture providing configured test container."""
    container = ServiceContainer()
    configure_test_services(container)
    return container

def test_integration_with_container(test_container):
    """Test using the container fixture."""
    service = test_container.resolve(ScrapingService)
    result = service.create_job('test-template', 'http://example.com')
    assert result is not None
```

## Advanced Container Features

### Lazy Loading

Services can be loaded lazily to improve startup time:

```python
class LazyServiceContainer(ServiceContainer):
    """Service container with lazy loading capabilities."""
    
    def __init__(self):
        super().__init__()
        self._lazy_services: Dict[Type, Callable] = {}
    
    def register_lazy(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register a service for lazy loading."""
        self._lazy_services[interface] = factory
    
    def resolve(self, interface: Type[T]) -> T:
        """Resolve service with lazy loading support."""
        # Check for lazy services first
        if interface in self._lazy_services and interface not in self._singletons:
            factory = self._lazy_services[interface]
            instance = factory()
            self._singletons[interface] = instance
            return instance
        
        # Fall back to parent implementation
        return super().resolve(interface)

# Usage
container.register_lazy(
    HeavyService,
    lambda: HeavyService(expensive_initialization=True)
)
```

### Service Decorators

Automatic registration using decorators:

```python
def service(interface: Type = None, singleton: bool = True):
    """Decorator for automatic service registration."""
    def decorator(cls):
        target_interface = interface or cls
        
        if singleton:
            container.register_singleton(target_interface, cls)
        else:
            container.register_factory(target_interface, cls)
        
        return cls
    return decorator

# Usage
@service(ScrapingService)
class ScrapingServiceImpl(ScrapingService):
    def __init__(self, template_manager: TemplateManager):
        self.template_manager = template_manager

@service()
class UtilityService:
    def helper_method(self):
        return "helper"
```

### Configuration Injection

Inject configuration values directly:

```python
class ConfigurableService:
    def __init__(self, database_url: str, api_key: str, max_retries: int):
        self.database_url = database_url
        self.api_key = api_key
        self.max_retries = max_retries

def create_configurable_service(config: AppConfig) -> ConfigurableService:
    """Factory that injects configuration values."""
    return ConfigurableService(
        database_url=config.database_url,
        api_key=config.api_key,
        max_retries=config.max_retries
    )

container.register_factory(ConfigurableService, create_configurable_service)
```

## Best Practices

### 1. Interface Design

Create clear, focused interfaces:

```python
# Good - single responsibility
class TemplateValidator(ABC):
    @abstractmethod
    def validate(self, template_data: Dict) -> ValidationResult:
        pass

# Avoid - too many responsibilities
class TemplateValidatorAndManagerAndProcessor(ABC):
    @abstractmethod
    def validate(self, template_data: Dict) -> ValidationResult:
        pass
    
    @abstractmethod
    def save_template(self, template_data: Dict) -> str:
        pass
    
    @abstractmethod
    def process_template(self, template_id: str) -> ProcessResult:
        pass
```

### 2. Constructor Injection

Prefer constructor injection over other methods:

```python
# Good - dependencies clear from constructor
class ScrapingService:
    def __init__(self, template_manager: TemplateManager, job_manager: JobManager):
        self.template_manager = template_manager
        self.job_manager = job_manager

# Avoid - hidden dependencies
class ScrapingService:
    def create_job(self, template_id: str):
        template_manager = container.resolve(TemplateManager)  # Hidden dependency
        job_manager = container.resolve(JobManager)            # Hidden dependency
```

### 3. Avoid Container Dependencies

Services shouldn't directly depend on the container:

```python
# Good - clean dependencies
class ScrapingService:
    def __init__(self, template_manager: TemplateManager):
        self.template_manager = template_manager

# Avoid - service knows about container
class ScrapingService:
    def __init__(self, container: ServiceContainer):
        self.container = container
    
    def create_job(self):
        template_manager = self.container.resolve(TemplateManager)
```

### 4. Lifecycle Management

Implement proper resource management:

```python
class DatabaseService(BaseService):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
    
    def initialize(self):
        """Initialize database connection."""
        self.connection = create_connection(self.connection_string)
    
    def cleanup(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
```

## Conclusion

ScraperV4's service container and dependency injection architecture provides a solid foundation for building maintainable, testable, and flexible applications. Key benefits include:

- **Separation of Concerns**: Clear boundaries between components
- **Testability**: Easy mocking and unit testing
- **Flexibility**: Can swap implementations without code changes
- **Maintainability**: Changes are isolated and predictable
- **Configuration**: Centralized service configuration

The container pattern scales from simple applications to complex enterprise systems, supporting ScraperV4's evolution from a desktop tool to a distributed scraping platform. Understanding and properly using this architecture is essential for anyone extending or maintaining ScraperV4.