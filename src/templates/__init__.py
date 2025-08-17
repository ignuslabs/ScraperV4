"""Self-healing template system for ScraperV4."""

from .template_manager import TemplateManager
from .template_validator import TemplateValidator
from .adaptive_selector import AdaptiveSelector

__all__ = ['TemplateManager', 'TemplateValidator', 'AdaptiveSelector']