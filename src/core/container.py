"""Service container for dependency injection in ScraperV4."""

from typing import TypeVar, Type, Dict, Any, Callable
import threading

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