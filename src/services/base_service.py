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
    
    def get_service(self, service_type):
        """Get a service instance from the container."""
        try:
            return container.resolve(service_type)
        except ValueError:
            return None