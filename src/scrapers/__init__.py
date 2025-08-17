"""Scrapling-based scraper framework."""

from .base_scraper import BaseScraper
from .template_scraper import TemplateScraper
from .stealth_fetcher import StealthFetcher

__all__ = ['BaseScraper', 'TemplateScraper', 'StealthFetcher']