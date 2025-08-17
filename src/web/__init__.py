"""Eel web interface integration for ScraperV4."""

from .eel_app import EelApp
from .api_routes import register_api_routes

__all__ = ['EelApp', 'register_api_routes']