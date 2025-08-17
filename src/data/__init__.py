"""File-based data storage for ScraperV4."""

from .job_manager import JobManager
from .template_manager import FileTemplateManager
from .result_storage import ResultStorage

__all__ = ['JobManager', 'FileTemplateManager', 'ResultStorage']